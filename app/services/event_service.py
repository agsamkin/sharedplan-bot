import logging
from datetime import date, time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

    Сортировка: event_date ASC, event_time ASC NULLS FIRST.
    """
    today = date.today()
    stmt = (
        select(Event)
        .where(Event.space_id == space_id, Event.event_date >= today)
        .order_by(Event.event_date.asc(), Event.event_time.asc().nullsfirst())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
