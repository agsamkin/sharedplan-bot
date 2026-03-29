import asyncio
import logging
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from alembic import command
from alembic.config import Config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text

from app.bot.callbacks import event_confirm as event_confirm_cb
from app.bot.callbacks import space_select as space_select_cb
from aiogram.types import MenuButtonWebApp, WebAppInfo
from app.bot.handlers import event, help, privacy, start, voice
from app.bot.commands import BOT_COMMANDS
from app.bot.middlewares.access_control import AccessControlMiddleware
from app.bot.middlewares.db_session import DbSessionMiddleware
from app.bot.middlewares.user_profile import UserProfileMiddleware
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

from app.db.engine import async_session
from app.scheduler.jobs import process_due_reminders, generate_recurring_occurrences
from mini_app.backend.app import create_web_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def check_db_connectivity() -> None:
    """Проверка связности с PostgreSQL (отдельный engine, чтобы не загрязнять основной pool)."""
    tmp_engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with tmp_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL: подключение успешно")
    except Exception as e:
        logger.critical("Не удалось подключиться к PostgreSQL: %s", e)
        sys.exit(1)
    finally:
        await tmp_engine.dispose()


def run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


async def main() -> None:
    # Проверка Telegram-токена
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    try:
        bot_info = await bot.get_me()
    except Exception as e:
        logger.critical("Невалидный Telegram-токен: %s", e)
        sys.exit(1)

    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(AccessControlMiddleware())
    dp.update.middleware(UserProfileMiddleware())

    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(privacy.router)
    dp.include_router(event_confirm_cb.router)
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
    scheduler.add_job(
        generate_recurring_occurrences,
        "interval",
        hours=24,
        kwargs={"session_factory": async_session},
    )
    scheduler.start()
    logger.info("APScheduler запущен (интервал %ds)", settings.REMINDER_CHECK_INTERVAL_SECONDS)

    # Запускаем aiohttp веб-сервер для Mini App
    web_app = create_web_app(bot)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", settings.MINI_APP_PORT)
    await site.start()
    logger.info("Mini App веб-сервер запущен на порту %d", settings.MINI_APP_PORT)

    await bot.set_my_commands(BOT_COMMANDS)
    if settings.MINI_APP_URL:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="Открыть",
                web_app=WebAppInfo(url=settings.MINI_APP_URL),
            )
        )
    # Логирование доступности опциональных функций
    stt_status = "включён" if settings.NEXARA_API_KEY else "отключён"
    llm_status = "включён" if settings.OPENROUTER_API_KEY else "отключён"
    log_func = logger.info if settings.NEXARA_API_KEY and settings.OPENROUTER_API_KEY else logger.warning
    log_func("Функции: STT (Nexara) — %s, LLM-парсинг (OpenRouter) — %s", stt_status, llm_status)

    logger.info("Бот @%s запускается...", bot_info.username)
    try:
        await dp.start_polling(bot, bot_username=bot_info.username)
    finally:
        logger.info("Останавливаем Mini App веб-сервер...")
        await runner.cleanup()


if __name__ == "__main__":
    try:
        # 1. PostgreSQL connectivity check
        asyncio.run(check_db_connectivity())
        # 2. Alembic миграции (синхронно, вне event loop)
        logger.info("Применяю миграции...")
        run_migrations()
        # 3. Telegram token check + polling
        asyncio.run(main())
    except SystemExit:
        raise
    except Exception as e:
        logger.critical("Ошибка запуска: %s", e)
        sys.exit(1)
