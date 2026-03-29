import logging

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.models import Event
from app.services.reminder_service import format_reminder_message, get_due_reminders, mark_sent

logger = logging.getLogger(__name__)


async def process_due_reminders(
    bot: Bot,
    session_factory: async_sessionmaker,
) -> None:
    """Обработать наступившие напоминания: отправить сообщения и пометить как отправленные."""
    async with session_factory() as session:
        reminders = await get_due_reminders(session)
        if not reminders:
            return

        logger.info("Найдено %d наступивших напоминаний", len(reminders))

        for reminder, event_title, event_date, event_time, space_name, user_language in reminders:
            try:
                text = format_reminder_message(
                    event_title, event_date, event_time, space_name, reminder.reminder_type,
                    lang=user_language or "en",
                )
                await bot.send_message(reminder.user_id, text)
            except Exception as e:
                logger.warning(
                    "Не удалось отправить напоминание: user_id=%s reminder_id=%s error_type=%s error=%s",
                    reminder.user_id,
                    reminder.id,
                    type(e).__name__,
                    e,
                )
            finally:
                await mark_sent(session, reminder.id)

        await session.commit()


async def generate_recurring_occurrences(
    session_factory: async_sessionmaker,
) -> None:
    """Генерировать недостающие вхождения повторяющихся событий на 60 дней вперёд."""
    from app.services.recurrence_service import advance_parent_date, generate_occurrences
    from sqlalchemy import select

    async with session_factory() as session:
        # Найти все родительские повторяющиеся события
        stmt = select(Event).where(
            Event.recurrence_rule.isnot(None),
            Event.parent_event_id.is_(None),
        )
        result = await session.execute(stmt)
        parent_events = result.scalars().all()

        if not parent_events:
            return

        logger.info("Генерация вхождений для %d повторяющихся событий", len(parent_events))

        total = 0
        for event in parent_events:
            try:
                await advance_parent_date(session, event)
                count = await generate_occurrences(session, event)
                total += count
            except Exception as e:
                logger.warning(
                    "Ошибка генерации вхождений для события %s: %s",
                    event.id, e,
                )

        await session.commit()
        if total:
            logger.info("Создано %d новых вхождений", total)
