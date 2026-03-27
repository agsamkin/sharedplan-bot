import logging
from datetime import date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from zoneinfo import ZoneInfo

from app.config import settings
from app.db.models import Event, ScheduledReminder, Space, User, UserSpace

logger = logging.getLogger(__name__)

REMINDER_LABELS = {
    "1d": "За 1 день",
    "2h": "За 2 часа",
    "1h": "За 1 час",
    "30m": "За 30 минут",
    "15m": "За 15 минут",
    "0m": "В момент события",
}

RELATIVE_LABELS = {
    "1d": "Завтра",
    "2h": "Через 2 часа",
    "1h": "Через 1 час",
    "30m": "Через 30 минут",
    "15m": "Через 15 минут",
    "0m": "Сейчас",
}

OFFSETS = {
    "1d": timedelta(days=1),
    "2h": timedelta(hours=2),
    "1h": timedelta(hours=1),
    "30m": timedelta(minutes=30),
    "15m": timedelta(minutes=15),
    "0m": timedelta(),
}

VALID_KEYS = set(REMINDER_LABELS.keys())


async def create_reminders_for_event(
    session: AsyncSession,
    event: Event,
    space_id: UUID,
) -> int:
    """Создать записи scheduled_reminders для всех участников пространства.

    Возвращает количество созданных напоминаний.
    """
    tz = ZoneInfo(settings.TIMEZONE)
    now = datetime.now(tz)

    # Загрузить участников с их reminder_settings
    stmt = (
        select(User.id, User.reminder_settings)
        .join(UserSpace, User.id == UserSpace.user_id)
        .where(UserSpace.space_id == space_id)
    )
    rows = (await session.execute(stmt)).all()

    count = 0
    for row in rows:
        user_id = row.id
        user_settings = row.reminder_settings or {}

        if event.event_time is None:
            # Только напоминание 1d на 09:00 накануне
            if not user_settings.get("1d", False):
                continue
            remind_at = datetime.combine(
                event.event_date - timedelta(days=1),
                time(9, 0),
                tzinfo=tz,
            )
            if remind_at <= now:
                continue
            session.add(ScheduledReminder(
                event_id=event.id,
                user_id=user_id,
                remind_at=remind_at,
                reminder_type="1d",
            ))
            count += 1
        else:
            event_dt = datetime.combine(event.event_date, event.event_time, tzinfo=tz)
            for key, offset in OFFSETS.items():
                if not user_settings.get(key, False):
                    continue
                remind_at = event_dt - offset
                if remind_at <= now:
                    continue
                session.add(ScheduledReminder(
                    event_id=event.id,
                    user_id=user_id,
                    remind_at=remind_at,
                    reminder_type=key,
                ))
                count += 1

    await session.flush()
    logger.info("Создано %d напоминаний для события %s", count, event.id)
    return count


async def get_due_reminders(session: AsyncSession, limit: int = 50) -> list:
    """Запросить неотправленные напоминания с наступившим remind_at.

    Возвращает список (reminder, event_title, event_date, event_time, space_name).
    """
    tz = ZoneInfo(settings.TIMEZONE)
    now = datetime.now(tz)

    stmt = (
        select(
            ScheduledReminder,
            Event.title,
            Event.event_date,
            Event.event_time,
            Space.name.label("space_name"),
        )
        .join(Event, ScheduledReminder.event_id == Event.id)
        .join(Space, Event.space_id == Space.id)
        .where(
            ScheduledReminder.sent.is_(False),
            ScheduledReminder.remind_at <= now,
        )
        .order_by(ScheduledReminder.remind_at)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.all())


async def mark_sent(session: AsyncSession, reminder_id: UUID) -> None:
    """Пометить напоминание как отправленное."""
    reminder = await session.get(ScheduledReminder, reminder_id)
    if reminder:
        reminder.sent = True
        await session.flush()


def format_reminder_message(
    event_title: str,
    event_date: date,
    event_time: time | None,
    space_name: str,
    reminder_type: str,
) -> str:
    """Форматировать текст Telegram-сообщения напоминания."""
    from app.bot.formatting import format_date_short_with_weekday

    relative = RELATIVE_LABELS.get(reminder_type, reminder_type)
    lines = ["🔔 Напоминание!\n", f"📝 {event_title}"]

    if event_time is None:
        # Событие без времени (только 1d): «Завтра, 5 апреля»
        date_str = format_date_short_with_weekday(event_date)
        lines.append(f"📅 {relative}, {date_str}")
    elif reminder_type == "1d":
        # За 1 день с временем: «Завтра в 19:00»
        time_str = event_time.strftime("%H:%M")
        lines.append(f"⏰ {relative} в {time_str}")
        lines.append(f"📅 {format_date_short_with_weekday(event_date)}")
    elif reminder_type == "0m":
        # В момент события: «Сейчас (14:00)»
        time_str = event_time.strftime("%H:%M")
        lines.append(f"⏰ {relative} ({time_str})")
        lines.append(f"📅 {format_date_short_with_weekday(event_date)}")
    else:
        # Обычное напоминание: «Через 15 минут (19:00)»
        time_str = event_time.strftime("%H:%M")
        lines.append(f"⏰ {relative} ({time_str})")
        lines.append(f"📅 {format_date_short_with_weekday(event_date)}")

    lines.append(f"📍 Пространство: {space_name}")
    return "\n".join(lines)
