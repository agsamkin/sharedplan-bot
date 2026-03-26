import logging
from dataclasses import dataclass
from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event

logger = logging.getLogger(__name__)


@dataclass
class ParsedEvent:
    title: str
    date: date
    time: time | None


async def parse_event_text(text: str) -> ParsedEvent:
    """Парсинг структурированного формата: название, ДД.ММ.ГГГГ[, ЧЧ:ММ].

    Raises ValueError при невалидном формате.
    """
    parts = [p.strip() for p in text.split(",")]
    if len(parts) < 2:
        raise ValueError(
            "Формат: название, ДД.ММ.ГГГГ, ЧЧ:ММ\n"
            "Время можно не указывать."
        )

    title = parts[0]
    if not title:
        raise ValueError("Название события не может быть пустым.")

    try:
        event_date = datetime.strptime(parts[1], "%d.%m.%Y").date()
    except ValueError:
        raise ValueError(
            f"Неверный формат даты: «{parts[1]}». Используй ДД.ММ.ГГГГ"
        )

    event_time: time | None = None
    if len(parts) >= 3 and parts[2]:
        try:
            event_time = datetime.strptime(parts[2], "%H:%M").time()
        except ValueError:
            raise ValueError(
                f"Неверный формат времени: «{parts[2]}». Используй ЧЧ:ММ"
            )

    return ParsedEvent(title=title, date=event_date, time=event_time)


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
