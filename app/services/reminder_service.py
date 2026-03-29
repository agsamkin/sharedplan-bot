import logging
from datetime import date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from zoneinfo import ZoneInfo

from app.config import settings
from app.db.models import Event, ScheduledReminder, Space, User, UserSpace
from app.i18n import get_relative_labels, t

logger = logging.getLogger(__name__)

OFFSETS = {
    "1d": timedelta(days=1),
    "2h": timedelta(hours=2),
    "1h": timedelta(hours=1),
    "30m": timedelta(minutes=30),
    "15m": timedelta(minutes=15),
    "0m": timedelta(),
}

VALID_KEYS = {"1d", "2h", "1h", "30m", "15m", "0m"}


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


async def recreate_reminders_for_event(
    session: AsyncSession,
    event: Event,
    space_id: UUID,
) -> int:
    """Удалить неотправленные напоминания и создать новые."""
    stmt = delete(ScheduledReminder).where(
        ScheduledReminder.event_id == event.id,
        ScheduledReminder.sent.is_(False),
    )
    await session.execute(stmt)
    await session.flush()
    return await create_reminders_for_event(session, event, space_id)


async def get_due_reminders(session: AsyncSession, limit: int = 50) -> list:
    """Запросить неотправленные напоминания с наступившим remind_at.

    Возвращает список (reminder, event_title, event_date, event_time, space_name, user_language).
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
            User.language.label("user_language"),
        )
        .join(Event, ScheduledReminder.event_id == Event.id)
        .join(Space, Event.space_id == Space.id)
        .join(User, ScheduledReminder.user_id == User.id)
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
    lang: str = "ru",
) -> str:
    """Форматировать текст Telegram-сообщения напоминания."""
    from app.bot.formatting import format_date_short_with_weekday

    relative_labels = get_relative_labels(lang)
    relative = relative_labels.get(reminder_type, reminder_type)
    lines = [t(lang, "reminder.message.header"), f"📝 {event_title}"]

    if event_time is None:
        date_str = format_date_short_with_weekday(event_date, lang)
        lines.append(f"📅 {relative}, {date_str}")
    elif reminder_type == "1d":
        time_str = event_time.strftime("%H:%M")
        lines.append(f"⏰ {relative} в {time_str}" if lang == "ru" else f"⏰ {relative} at {time_str}")
        lines.append(f"📅 {format_date_short_with_weekday(event_date, lang)}")
    elif reminder_type == "0m":
        time_str = event_time.strftime("%H:%M")
        lines.append(f"⏰ {relative} ({time_str})")
        lines.append(f"📅 {format_date_short_with_weekday(event_date, lang)}")
    else:
        time_str = event_time.strftime("%H:%M")
        lines.append(f"⏰ {relative} ({time_str})")
        lines.append(f"📅 {format_date_short_with_weekday(event_date, lang)}")

    lines.append(t(lang, "reminder.message.space", name=space_name))
    return "\n".join(lines)
