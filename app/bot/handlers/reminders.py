from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.reminder_settings import reminder_settings_keyboard
from app.db.models import User

router = Router()


@router.message(Command("reminders"))
async def cmd_reminders(message: Message, session: AsyncSession) -> None:
    user = await session.get(User, message.from_user.id)
    if not user:
        await message.answer("Сначала используй /start")
        return

    settings = user.reminder_settings or {}
    await message.answer(
        "⏰ Настройки напоминаний:\n\nВыбери, за сколько до события напоминать:",
        reply_markup=reminder_settings_keyboard(settings),
    )
