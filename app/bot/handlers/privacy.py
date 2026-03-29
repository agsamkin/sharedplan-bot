import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.i18n import t

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("privacy"))
async def cmd_privacy(message: Message, lang: str = "en") -> None:
    logger.info("/privacy user_id=%d", message.from_user.id)
    await message.answer(t(lang, "privacy.text"))
