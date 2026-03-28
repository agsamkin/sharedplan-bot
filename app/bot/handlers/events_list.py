import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services import space_service

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("events"))
async def cmd_events(message: Message, session: AsyncSession) -> None:
    logger.info("/events user_id=%d", message.from_user.id)
    spaces = await space_service.get_user_spaces(session, message.from_user.id)

    if not spaces:
        await message.answer(
            "У тебя пока нет пространств. Создай первое через /newspace!"
        )
        return

    if settings.MINI_APP_URL:
        await message.answer(
            "Открой приложение для просмотра и управления событиями:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="📅 Открыть событ��я",
                    web_app=WebAppInfo(url=settings.MINI_APP_URL),
                )]
            ]),
        )
    else:
        await message.answer("Mini App пока не настроен. Используй /app после настройки.")
