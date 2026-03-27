from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DEFAULT_REMINDER_SETTINGS, User


class UserProfileMiddleware(BaseMiddleware):
    """Обновляет first_name и username пользователя при каждом взаимодействии."""

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
            stmt = pg_insert(User).values(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                reminder_settings=DEFAULT_REMINDER_SETTINGS,
            ).on_conflict_do_update(
                index_elements=[User.id],
                set_={
                    "first_name": user.first_name,
                    "username": user.username,
                },
            )
            await session.execute(stmt)

        return await handler(event, data)
