import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.i18n import t

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str = "en") -> None:
    logger.info("/help user_id=%d", message.from_user.id)
    await message.answer(t(lang, "help.text"))
