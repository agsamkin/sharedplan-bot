import logging
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from zoneinfo import ZoneInfo

from app.config import settings
from app.db.models import Event
from app.services import reminder_service

logger = logging.getLogger(__name__)

VALID_RECURRENCE_RULES = {"daily", "weekly", "biweekly", "monthly", "yearly"}


def next_occurrence_date(current_date: date, rule: str) -> date:
    """Вычислить следующую дату повторения на основе правила рекуррентности."""
    if rule == "daily":
        return current_date + timedelta(days=1)
    elif rule == "weekly":
        return current_date + timedelta(days=7)
    elif rule == "biweekly":
        return current_date + timedelta(days=14)
    elif rule == "monthly":
        return current_date + relativedelta(months=1)
    elif rule == "yearly":
        return current_date + relativedelta(years=1)
    else:
        raise ValueError(f"Неизвестное правило рекуррентности: {rule}")


async def advance_parent_date(
    session: AsyncSession,
    event: Event,
) -> bool:
    """Прокрутить event_date родительского события на ближайшую будущую дату.

    Если event_date уже в будущем — ничего не делает.
    Идемпотентна, безопасна при конкурентных вызовах.
    Возвращает True если дата была изменена.
    """
    if event.recurrence_rule is None or event.parent_event_id is not None:
        return False

    tz = ZoneInfo(settings.TIMEZONE)
    now = datetime.now(tz)
    today = now.date()

    # Проверить, нужна ли прокрутка
    if event.event_date > today:
        return False
    if event.event_date == today:
        if event.event_time is None or event.event_time >= now.time():
            return False

    # Шагаем вперёд до будущей даты
    rule = event.recurrence_rule
    target = next_occurrence_date(event.event_date, rule)
    while target < today:
        target = next_occurrence_date(target, rule)
    # Если target = сегодня, но время уже прошло — ещё один шаг
    if target == today and event.event_time is not None and event.event_time < now.time():
        target = next_occurrence_date(target, rule)

    event.event_date = target
    await session.flush()

    logger.info(
        "Прокручена дата события %s → %s (правило: %s)",
        event.id, target, rule,
    )
    return True


async def generate_occurrences(
    session: AsyncSession,
    event: Event,
    horizon_days: int = 60,
) -> int:
    """Сгенерировать дочерние вхождения для повторяющегося события.

    Работает только для родительских событий (recurrence_rule не None,
    parent_event_id is None). Генерирует даты от event.event_date
    с шагом по правилу до current_date + horizon_days.

    Возвращает количество созданных вхождений.
    """
    if event.recurrence_rule is None or event.parent_event_id is not None:
        return 0

    tz = ZoneInfo(settings.TIMEZONE)
    today = datetime.now(tz).date()
    horizon = today + timedelta(days=horizon_days)

    rule = event.recurrence_rule

    # Вычислить все целевые даты заранее
    target_dates = []
    target_date = next_occurrence_date(event.event_date, rule)
    while target_date <= horizon:
        target_dates.append(target_date)
        target_date = next_occurrence_date(target_date, rule)

    if not target_dates:
        return 0

    # Batch-проверка существующих вхождений (1 запрос вместо N)
    stmt = select(Event.event_date).where(
        Event.parent_event_id == event.id,
        Event.event_date.in_(target_dates),
    )
    existing_dates = set((await session.execute(stmt)).scalars().all())

    # Создать только отсутствующие вхождения
    new_occurrences = []
    for td in target_dates:
        if td not in existing_dates:
            occurrence = Event(
                space_id=event.space_id,
                title=event.title,
                event_date=td,
                event_time=event.event_time,
                created_by=event.created_by,
                raw_input=None,
                recurrence_rule=None,
                parent_event_id=event.id,
            )
            session.add(occurrence)
            new_occurrences.append(occurrence)

    if new_occurrences:
        await session.flush()  # Один flush вместо N

        for occurrence in new_occurrences:
            await reminder_service.create_reminders_for_event(
                session, occurrence, event.space_id,
            )
            logger.debug(
                "Создано вхождение %s на %s для события %s",
                occurrence.id, occurrence.event_date, event.id,
            )

    count = len(new_occurrences)
    logger.info(
        "Сгенерировано %d вхождений для события %s (горизонт %d дней)",
        count, event.id, horizon_days,
    )
    return count


async def regenerate_occurrences(
    session: AsyncSession,
    parent_event: Event,
    horizon_days: int = 60,
) -> int:
    """Удалить будущие дочерние события и создать заново.

    Удаляет все дочерние события с event_date >= сегодня,
    затем вызывает generate_occurrences для создания новых.

    Возвращает количество созданных вхождений.
    """
    tz = ZoneInfo(settings.TIMEZONE)
    today = datetime.now(tz).date()

    stmt = delete(Event).where(
        Event.parent_event_id == parent_event.id,
        Event.event_date >= today,
    )
    await session.execute(stmt)
    await session.flush()

    return await generate_occurrences(session, parent_event, horizon_days)


async def update_future_occurrences(
    session: AsyncSession,
    parent_event: Event,
) -> int:
    """Обновить будущие дочерние события при изменении родительского.

    Обновляет title и event_time у дочерних событий с event_date >= сегодня.
    Пересоздаёт напоминания для каждого обновлённого вхождения.

    Возвращает количество обновлённых вхождений.
    """
    tz = ZoneInfo(settings.TIMEZONE)
    today = datetime.now(tz).date()

    # Обновить title и event_time
    stmt = (
        update(Event)
        .where(
            Event.parent_event_id == parent_event.id,
            Event.event_date >= today,
        )
        .values(
            title=parent_event.title,
            event_time=parent_event.event_time,
        )
    )
    result = await session.execute(stmt)
    await session.flush()

    updated_count = result.rowcount

    # Пересоздать напоминания для обновлённых вхождений
    stmt_select = select(Event).where(
        Event.parent_event_id == parent_event.id,
        Event.event_date >= today,
    )
    occurrences = (await session.execute(stmt_select)).scalars().all()

    for occurrence in occurrences:
        await reminder_service.recreate_reminders_for_event(
            session, occurrence, parent_event.space_id,
        )

    logger.info(
        "Обновлено %d будущих вхождений для события %s",
        updated_count, parent_event.id,
    )
    return updated_count
