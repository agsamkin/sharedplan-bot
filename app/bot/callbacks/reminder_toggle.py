import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.reminder_settings import reminder_settings_keyboard
from app.db.models import User
from app.services.reminder_service import VALID_KEYS

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("reminder_toggle:"))
async def on_reminder_toggle(callback: CallbackQuery, session: AsyncSession) -> None:
    key = callback.data.split(":", 1)[1]
    if key not in VALID_KEYS:
        logger.warning("Невалидный ключ напоминания: %s", key)
        await callback.answer()
        return

    user = await session.get(User, callback.from_user.id)
    if not user:
        await callback.answer("Пользователь не найден")
        return

    settings = dict(user.reminder_settings or {})
    settings[key] = not settings.get(key, False)
    user.reminder_settings = settings
    await session.flush()

    await callback.message.edit_reply_markup(
        reply_markup=reminder_settings_keyboard(settings),
    )
    await callback.answer()
