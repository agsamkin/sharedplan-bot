import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    logger.info("/help user_id=%d", message.from_user.id)
    await message.answer(
        "/start — Начать работу с ботом\n"
        "/help — Список команд\n"
        "/newspace — Создать новое пространство\n"
        "/spaces — Мои пространства\n"
        "/space_info — Информация о пространстве\n"
        "/events — Ближайшие события\n"
        "/reminders — Настройки напоминаний"
    )
