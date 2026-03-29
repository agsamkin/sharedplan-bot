from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DEFAULT_REMINDER_SETTINGS, User
from app.i18n import normalize_language


class UserProfileMiddleware(BaseMiddleware):
    """Обновляет first_name и username пользователя при каждом взаимодействии.

    При создании нового пользователя определяет язык из language_code Telegram.
    Для существующих — не перезаписывает language.
    Передаёт data["lang"] для использования в хендлерах.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession | None = data.get("session")
        if session is None:
            return await handler(event, data)

        user = None
        if isinstance(event, Update):
            if event.message and event.message.from_user:
                user = event.message.from_user
            elif event.callback_query and event.callback_query.from_user:
                user = event.callback_query.from_user

        if user is not None:
            detected_lang = normalize_language(user.language_code)

            stmt = pg_insert(User).values(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                reminder_settings=DEFAULT_REMINDER_SETTINGS,
                language=detected_lang,
            ).on_conflict_do_update(
                index_elements=[User.id],
                set_={
                    "first_name": user.first_name,
                    "username": user.username,
                },
            )
            await session.execute(stmt)

            # Получаем актуальный язык из БД (не перезаписанный)
            result = await session.execute(
                select(User.language).where(User.id == user.id)
            )
            lang = result.scalar_one_or_none() or "en"
            data["lang"] = lang
        else:
            data["lang"] = "en"

        return await handler(event, data)
