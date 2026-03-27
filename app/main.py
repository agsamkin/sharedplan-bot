import asyncio
import logging

from aiogram import Bot, Dispatcher
from alembic import command
from alembic.config import Config
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.callbacks import event_confirm as event_confirm_cb
from app.bot.callbacks import reminder_toggle as reminder_toggle_cb
from app.bot.callbacks import space_select as space_select_cb
from app.bot.handlers import event, events_list, help, reminders, space, start, voice
from app.bot.commands import BOT_COMMANDS
from app.bot.middlewares.db_session import DbSessionMiddleware
from app.config import settings
from app.db.engine import async_session
from app.scheduler.jobs import process_due_reminders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


async def main() -> None:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware())

    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(space.router)
    dp.include_router(events_list.router)
    dp.include_router(reminders.router)
    dp.include_router(event_confirm_cb.router)
    dp.include_router(reminder_toggle_cb.router)
    dp.include_router(space_select_cb.router)
    dp.include_router(voice.router)
    dp.include_router(event.router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        process_due_reminders,
        "interval",
        seconds=settings.REMINDER_CHECK_INTERVAL_SECONDS,
        kwargs={"bot": bot, "session_factory": async_session},
    )
    scheduler.start()
    logger.info("APScheduler запущен (интервал %ds)", settings.REMINDER_CHECK_INTERVAL_SECONDS)

    bot_info = await bot.get_me()
    await bot.set_my_commands(BOT_COMMANDS)
    logger.info("Бот @%s запускается...", bot_info.username)
    await dp.start_polling(bot, bot_username=bot_info.username)


if __name__ == "__main__":
    logger.info("Применяю миграции...")
    run_migrations()
    asyncio.run(main())
