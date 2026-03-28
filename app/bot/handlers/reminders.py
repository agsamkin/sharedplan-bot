import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from app.config import settings

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("reminders"))
async def cmd_reminders(message: Message) -> None:
    logger.info("/reminders user_id=%d", message.from_user.id)
    if settings.MINI_APP_URL:
        url = settings.MINI_APP_URL.rstrip("/") + "/settings/reminders"
        await message.answer(
            "Настрой напоминания в приложении:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="⏰ Настройки напоминаний",
                    web_app=WebAppInfo(url=url),
                )]
            ]),
        )
    else:
        await message.answer("Mini App пока не настроен.")
