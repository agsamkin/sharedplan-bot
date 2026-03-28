import logging
from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy import and_, delete, or_, select
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


async def get_upcoming_events(
    session: AsyncSession, space_id: UUID, limit: int = 10
) -> list[Event]:
    """Получить ближайшие будущие события пространства.

    Исключает события с прошедшим временем (для сегодняшних).
    Сортировка: event_date ASC, event_time ASC NULLS FIRST.
    """
    tz = ZoneInfo(settings.TIMEZONE)
    now = datetime.now(tz)
    today = now.date()
    current_time = now.time()

    stmt = (
        select(Event)
        .where(
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
        )
        .order_by(Event.event_date.asc(), Event.event_time.asc().nullsfirst())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


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
