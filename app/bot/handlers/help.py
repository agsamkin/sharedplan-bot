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
        "📅 Создание событий\n"
        "Просто напиши или надиктуй событие — я распознаю дату и время.\n"
        "Например: «Ужин завтра в 19:00» или «День рождения Ани 5 апреля».\n\n"
        "📱 Управление\n"
        "Пространства, события и напоминания — в приложении.\n"
        "Нажми кнопку меню слева от поля ввода.\n\n"
        "Команды:\n"
        "/help — Эта справка\n"
        "/privacy — Политика конфиденциальности"
    )
