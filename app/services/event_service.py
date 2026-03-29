import logging
from datetime import date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from zoneinfo import ZoneInfo

from app.config import settings
from app.db.models import Event

logger = logging.getLogger(__name__)


async def create_event(
    session: AsyncSession,
    space_id: UUID,
    title: str,
    event_date: date,
    event_time: time | None,
    created_by: int,
    raw_input: str | None = None,
) -> Event:
    """Создать событие в пространстве."""
    event = Event(
        space_id=space_id,
        title=title,
        event_date=event_date,
        event_time=event_time,
        created_by=created_by,
        raw_input=raw_input,
    )
    session.add(event)
    await session.flush()
    return event


def _upcoming_events_filter(space_id: UUID):
    """Общий фильтр для предстоящих событий пространства."""
    tz = ZoneInfo(settings.TIMEZONE)
    now = datetime.now(tz)
    today = now.date()
    current_time = now.time()

    return [
        Event.space_id == space_id,
        or_(
            Event.event_date > today,
            and_(
                Event.event_date == today,
                or_(
                    Event.event_time.is_(None),
                    Event.event_time >= current_time,
                ),
            ),
        ),
    ]


async def get_upcoming_events(
    session: AsyncSession, space_id: UUID, limit: int
) -> list[Event]:
    """Получить ближайшие будущие события пространства.

    Исключает события с прошедшим временем (для сегодняшних).
    Сортировка: event_date ASC, event_time ASC NULLS FIRST.
    """
    stmt = (
        select(Event)
        .where(*_upcoming_events_filter(space_id))
        .order_by(Event.event_date.asc(), Event.event_time.asc().nullsfirst())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def count_upcoming_events(session: AsyncSession, space_id: UUID) -> int:
    """Подсчитать общее количество предстоящих событий пространства."""
    stmt = select(func.count()).select_from(Event).where(
        *_upcoming_events_filter(space_id)
    )
    return await session.scalar(stmt) or 0


async def get_event_for_owner(
    session: AsyncSession, event_id: UUID, user_id: int
) -> Event | None:
    """Получить событие, только если пользователь — его владелец."""
    stmt = select(Event).where(Event.id == event_id, Event.created_by == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def delete_event(session: AsyncSession, event_id: UUID) -> None:
    """Удалить событие (каскадно удаляет напоминания)."""
    stmt = delete(Event).where(Event.id == event_id)
    await session.execute(stmt)
    await session.flush()


async def find_conflicting_events(
    session: AsyncSession,
    space_id: UUID,
    event_date: date,
    event_time: time | None,
    exclude_event_id: UUID | None = None,
) -> list[Event]:
    """Найти события в пространстве, пересекающиеся по времени (+-2 часа)."""
    if event_time is None:
        return []

    event_dt = datetime.combine(event_date, event_time)
    day_start = datetime.combine(event_date, time(0, 0))
    day_end = datetime.combine(event_date, time(23, 59, 59))
    window_start = max(event_dt - timedelta(hours=2), day_start).time()
    window_end = min(event_dt + timedelta(hours=2), day_end).time()

    conditions = [
        Event.space_id == space_id,
        Event.event_date == event_date,
        Event.event_time.isnot(None),
        Event.event_time > window_start,
        Event.event_time < window_end,
    ]

    if exclude_event_id is not None:
        conditions.append(Event.id != exclude_event_id)

    stmt = (
        select(Event)
        .where(*conditions)
        .order_by(Event.event_time.asc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_event(
    session: AsyncSession, event_id: UUID, **fields
) -> Event | None:
    """Обновить поля события (title, event_date, event_time)."""
    event = await session.get(Event, event_id)
    if not event:
        return None
    for key, value in fields.items():
        setattr(event, key, value)
    await session.flush()
    return event
