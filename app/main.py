import asyncio
import logging

from aiogram import Bot, Dispatcher
from alembic import command
from alembic.config import Config

from app.bot.callbacks import space_select as space_select_cb
from app.bot.handlers import help, space, start
from app.bot.middlewares.db_session import DbSessionMiddleware
from app.config import settings

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
    dp.include_router(space_select_cb.router)

    bot_info = await bot.get_me()
    logger.info("Бот @%s запускается...", bot_info.username)
    await dp.start_polling(bot, bot_username=bot_info.username)


if __name__ == "__main__":
    logger.info("Применяю миграции...")
    run_migrations()
    asyncio.run(main())
