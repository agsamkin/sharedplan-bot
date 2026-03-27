import logging

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

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

        for reminder, event_title, event_date, event_time, space_name in reminders:
            try:
                text = format_reminder_message(
                    event_title, event_date, event_time, space_name, reminder.reminder_type,
                )
                await bot.send_message(reminder.user_id, text)
            except Exception:
                logger.warning(
                    "Не удалось отправить напоминание пользователю %s (reminder %s)",
                    reminder.user_id,
                    reminder.id,
                )
            finally:
                await mark_sent(session, reminder.id)

        await session.commit()
