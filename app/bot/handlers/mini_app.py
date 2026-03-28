import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from app.config import settings

logger = logging.getLogger(__name__)
router = Router()


def _webapp_button(text: str, path: str = "") -> InlineKeyboardMarkup:
    """Создать inline-клавиатуру с WebApp-кнопкой."""
    url = settings.MINI_APP_URL.rstrip("/") + path if settings.MINI_APP_URL else ""
    if not url:
        return InlineKeyboardMarkup(inline_keyboard=[])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))]
    ])


@router.message(Command("app"))
async def cmd_app(message: Message) -> None:
    logger.info("/app user_id=%d", message.from_user.id)
    if not settings.MINI_APP_URL:
        await message.answer("Mini App пока не настроен.")
        return
    await message.answer(
        "📱 Открой приложение для управления событиями и пространствами:",
        reply_markup=_webapp_button("📱 Открыть приложение"),
    )
