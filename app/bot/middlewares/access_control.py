import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import UserSpace
from app.i18n import t

logger = logging.getLogger(__name__)


class AccessControlMiddleware(BaseMiddleware):
    """Блокирует взаимодействие с ботом для неавторизованных пользователей.

    Авторизованы: владелец (OWNER_TELEGRAM_ID) и участники хотя бы одного пространства.
    Исключение: deep link ``/start join_*`` пропускается для всех (механизм вступления).
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Update):
            return await handler(event, data)

        user_id = self._extract_user_id(event)
        if user_id is None:
            return await handler(event, data)

        # Владелец всегда авторизован
        if user_id == settings.OWNER_TELEGRAM_ID:
            return await handler(event, data)

        # Deep link join пропускается для всех
        if self._is_join_deeplink(event):
            return await handler(event, data)

        lang = data.get("lang", "en")

        # Проверка членства в пространстве
        session: AsyncSession | None = data.get("session")
        if session is None:
            logger.error("AccessControlMiddleware: session отсутствует в data")
            return None

        try:
            is_member = await self._has_any_space(session, user_id)
        except Exception:
            logger.exception("Ошибка проверки доступа для user_id=%d", user_id)
            await self._send_error(event, lang)
            return None

        if is_member:
            return await handler(event, data)

        # Неавторизованный пользователь
        await self._send_private_message(event, lang)
        return None

    @staticmethod
    def _extract_user_id(event: Update) -> int | None:
        if event.message and event.message.from_user:
            return event.message.from_user.id
        if event.callback_query and event.callback_query.from_user:
            return event.callback_query.from_user.id
        return None

    @staticmethod
    def _is_join_deeplink(event: Update) -> bool:
        if event.message and event.message.text:
            return event.message.text.startswith("/start join_")
        return False

    @staticmethod
    async def _has_any_space(session: AsyncSession, user_id: int) -> bool:
        stmt = select(UserSpace.user_id).where(UserSpace.user_id == user_id).limit(1)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def _send_private_message(event: Update, lang: str = "en") -> None:
        if event.message:
            await event.message.answer(t(lang, "access.private_bot"))
        elif event.callback_query:
            await event.callback_query.answer(
                text=t(lang, "access.denied"), show_alert=True,
            )

    @staticmethod
    async def _send_error(event: Update, lang: str = "en") -> None:
        if event.message:
            await event.message.answer(t(lang, "access.error"))
        elif event.callback_query:
            await event.callback_query.answer(
                text=t(lang, "access.error_short"), show_alert=True,
            )
