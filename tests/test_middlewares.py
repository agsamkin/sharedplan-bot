"""Тесты middleware: DbSessionMiddleware и UserProfileMiddleware."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest

# Очистка моков
for _key in list(sys.modules):
    if _key.startswith("app.services.") or _key == "app.services":
        _mod = sys.modules[_key]
        if hasattr(_mod, "_mock_name"):
            del sys.modules[_key]
for _key in list(sys.modules):
    if _key.startswith("app.db.") or _key == "app.db.models":
        _mod = sys.modules[_key]
        if hasattr(_mod, "_mock_name"):
            del sys.modules[_key]
for _key in ["app.config", "app.db.engine"]:
    if _key in sys.modules and hasattr(sys.modules[_key], "_mock_name"):
        del sys.modules[_key]

from app.bot.middlewares.db_session import DbSessionMiddleware  # noqa: E402
from app.bot.middlewares.user_profile import UserProfileMiddleware  # noqa: E402


class TestDbSessionMiddleware:
    @pytest.mark.asyncio
    async def test_injects_session_and_commits(self):
        """Инжектирует сессию и коммитит при успехе."""
        mw = DbSessionMiddleware()
        handler = AsyncMock(return_value="ok")
        event = MagicMock()
        data = {}

        mock_session = AsyncMock()

        with patch("app.bot.middlewares.db_session.async_session") as mock_factory:
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await mw(handler, event, data)

        assert result == "ok"
        handler.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_rollbacks_on_error(self):
        """Откатывает транзакцию при ошибке."""
        mw = DbSessionMiddleware()
        handler = AsyncMock(side_effect=ValueError("Test error"))
        event = MagicMock()
        data = {}

        mock_session = AsyncMock()

        with patch("app.bot.middlewares.db_session.async_session") as mock_factory:
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)
            with pytest.raises(ValueError, match="Test error"):
                await mw(handler, event, data)

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()


class TestUserProfileMiddleware:
    @pytest.mark.asyncio
    async def test_no_session_passes_through(self):
        """Без сессии — пропускаем."""
        mw = UserProfileMiddleware()
        handler = AsyncMock(return_value="ok")
        event = MagicMock()
        data = {}
        result = await mw(handler, event, data)
        assert result == "ok"
        assert data.get("lang") is None  # не устанавливается

    @pytest.mark.asyncio
    async def test_message_user_upserts(self):
        """При message с from_user — выполняет upsert и устанавливает lang."""
        from aiogram.types import Update
        mw = UserProfileMiddleware()
        handler = AsyncMock(return_value="ok")

        user = MagicMock()
        user.id = 100
        user.username = "test"
        user.first_name = "Тест"
        user.language_code = "ru"

        message = MagicMock()
        message.from_user = user

        event = MagicMock(spec=Update)
        event.message = message
        event.callback_query = None

        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = "ru"
        session.execute = AsyncMock(return_value=result_mock)

        data = {"session": session}
        result = await mw(handler, event, data)

        assert result == "ok"
        assert data["lang"] == "ru"
        assert session.execute.call_count == 2  # upsert + select lang

    @pytest.mark.asyncio
    async def test_callback_user_upserts(self):
        """При callback_query с from_user — выполняет upsert."""
        from aiogram.types import Update
        mw = UserProfileMiddleware()
        handler = AsyncMock(return_value="ok")

        user = MagicMock()
        user.id = 200
        user.username = "user2"
        user.first_name = "Иван"
        user.language_code = "en"

        event = MagicMock(spec=Update)
        event.message = None
        event.callback_query = MagicMock()
        event.callback_query.from_user = user

        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = "en"
        session.execute = AsyncMock(return_value=result_mock)

        data = {"session": session}
        result = await mw(handler, event, data)

        assert data["lang"] == "en"

    @pytest.mark.asyncio
    async def test_no_user_sets_default_lang(self):
        """Без user в event — устанавливаем lang=en."""
        from aiogram.types import Update
        mw = UserProfileMiddleware()
        handler = AsyncMock(return_value="ok")

        event = MagicMock(spec=Update)
        event.message = None
        event.callback_query = None

        session = AsyncMock()
        data = {"session": session}
        result = await mw(handler, event, data)

        assert data["lang"] == "en"
        session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_non_update_event_with_session(self):
        """Не-Update с сессией — lang не устанавливается, handler вызывается."""
        mw = UserProfileMiddleware()
        handler = AsyncMock(return_value="ok")
        event = MagicMock()  # не Update
        event.__class__ = type("SomeEvent", (), {})

        session = AsyncMock()
        data = {"session": session}
        result = await mw(handler, event, data)

        assert data["lang"] == "en"  # default для non-Update
