"""Тесты middleware контроля доступа."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

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

from app.bot.middlewares.access_control import AccessControlMiddleware  # noqa: E402


def _make_update(user_id=100, text=None, is_callback=False):
    """Создать mock Update."""
    from aiogram.types import Update
    update = MagicMock(spec=Update)

    if is_callback:
        update.message = None
        update.callback_query = MagicMock()
        update.callback_query.from_user = MagicMock()
        update.callback_query.from_user.id = user_id
        update.callback_query.answer = AsyncMock()
    else:
        update.callback_query = None
        update.message = MagicMock()
        update.message.from_user = MagicMock()
        update.message.from_user.id = user_id
        update.message.text = text
        update.message.answer = AsyncMock()

    return update


class TestExtractUserId:
    def test_from_message(self):
        update = _make_update(user_id=42)
        result = AccessControlMiddleware._extract_user_id(update)
        assert result == 42

    def test_from_callback(self):
        update = _make_update(user_id=99, is_callback=True)
        result = AccessControlMiddleware._extract_user_id(update)
        assert result == 99

    def test_no_user(self):
        from aiogram.types import Update
        update = MagicMock(spec=Update)
        update.message = None
        update.callback_query = None
        result = AccessControlMiddleware._extract_user_id(update)
        assert result is None

    def test_message_no_from_user(self):
        from aiogram.types import Update
        update = MagicMock(spec=Update)
        update.message = MagicMock()
        update.message.from_user = None
        update.callback_query = None
        result = AccessControlMiddleware._extract_user_id(update)
        assert result is None


class TestIsJoinDeeplink:
    def test_join_deeplink(self):
        update = _make_update(text="/start join_abc123")
        assert AccessControlMiddleware._is_join_deeplink(update) is True

    def test_regular_start(self):
        update = _make_update(text="/start")
        assert AccessControlMiddleware._is_join_deeplink(update) is False

    def test_regular_text(self):
        update = _make_update(text="Hello")
        assert AccessControlMiddleware._is_join_deeplink(update) is False

    def test_callback_query(self):
        update = _make_update(is_callback=True)
        assert AccessControlMiddleware._is_join_deeplink(update) is False

    def test_no_message(self):
        from aiogram.types import Update
        update = MagicMock(spec=Update)
        update.message = None
        assert AccessControlMiddleware._is_join_deeplink(update) is False


class TestMiddlewareCall:
    @pytest.mark.asyncio
    async def test_non_update_passes_through(self):
        """Не-Update объект пропускается без проверки."""
        mw = AccessControlMiddleware()
        handler = AsyncMock(return_value="ok")
        event = MagicMock()  # не Update
        event.__class__ = type("SomeEvent", (), {})  # не isinstance(Update)
        data = {}
        result = await mw(handler, event, data)
        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_owner_always_passes(self):
        """Владелец бота всегда авторизован."""
        mw = AccessControlMiddleware()
        handler = AsyncMock(return_value="ok")
        update = _make_update(user_id=12345)
        data = {"session": AsyncMock(), "lang": "ru"}

        with patch("app.bot.middlewares.access_control.settings") as mock_settings:
            mock_settings.OWNER_TELEGRAM_ID = 12345
            result = await mw(handler, update, data)

        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_join_deeplink_passes(self):
        """Deep link join пропускается для всех."""
        mw = AccessControlMiddleware()
        handler = AsyncMock(return_value="ok")
        update = _make_update(user_id=999, text="/start join_abc")
        data = {"session": AsyncMock(), "lang": "ru"}

        with patch("app.bot.middlewares.access_control.settings") as mock_settings:
            mock_settings.OWNER_TELEGRAM_ID = 1  # не совпадает
            result = await mw(handler, update, data)

        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_member_passes(self):
        """Участник пространства авторизован."""
        mw = AccessControlMiddleware()
        handler = AsyncMock(return_value="ok")
        update = _make_update(user_id=200, text="Ужин завтра")
        session = AsyncMock()
        data = {"session": session, "lang": "ru"}

        mock_has = AsyncMock(return_value=True)
        with patch("app.bot.middlewares.access_control.settings") as mock_settings:
            mock_settings.OWNER_TELEGRAM_ID = 1
            with patch.object(AccessControlMiddleware, "_has_any_space", mock_has):
                result = await mw(handler, update, data)

        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_non_member_blocked(self):
        """Не-участник получает сообщение об ограниченном доступе."""
        mw = AccessControlMiddleware()
        handler = AsyncMock()
        update = _make_update(user_id=200, text="Hello")
        session = AsyncMock()
        data = {"session": session, "lang": "ru"}

        mock_has = AsyncMock(return_value=False)
        with patch("app.bot.middlewares.access_control.settings") as mock_settings:
            mock_settings.OWNER_TELEGRAM_ID = 1
            with patch.object(AccessControlMiddleware, "_has_any_space", mock_has):
                result = await mw(handler, update, data)

        handler.assert_not_called()
        update.message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_session_returns_none(self):
        """Без сессии в data — возвращает None."""
        mw = AccessControlMiddleware()
        handler = AsyncMock()
        update = _make_update(user_id=200, text="Hello")
        data = {"lang": "ru"}

        with patch("app.bot.middlewares.access_control.settings") as mock_settings:
            mock_settings.OWNER_TELEGRAM_ID = 1
            result = await mw(handler, update, data)

        assert result is None
        handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_callback_query_non_member_blocked(self):
        """Callback query от не-участника получает alert."""
        mw = AccessControlMiddleware()
        handler = AsyncMock()
        update = _make_update(user_id=200, is_callback=True)
        session = AsyncMock()
        data = {"session": session, "lang": "en"}

        mock_has = AsyncMock(return_value=False)
        with patch("app.bot.middlewares.access_control.settings") as mock_settings:
            mock_settings.OWNER_TELEGRAM_ID = 1
            with patch.object(AccessControlMiddleware, "_has_any_space", mock_has):
                result = await mw(handler, update, data)

        handler.assert_not_called()
        update.callback_query.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_db_error_sends_error_message(self):
        """Ошибка БД при проверке доступа — отправляет ошибку."""
        mw = AccessControlMiddleware()
        handler = AsyncMock()
        update = _make_update(user_id=200, text="Hello")
        session = AsyncMock()
        data = {"session": session, "lang": "ru"}

        mock_has = AsyncMock(side_effect=Exception("DB error"))
        with patch("app.bot.middlewares.access_control.settings") as mock_settings:
            mock_settings.OWNER_TELEGRAM_ID = 1
            with patch.object(AccessControlMiddleware, "_has_any_space", mock_has):
                result = await mw(handler, update, data)

        assert result is None
        handler.assert_not_called()
        update.message.answer.assert_called_once()


class TestSendPrivateMessage:
    @pytest.mark.asyncio
    async def test_message_answer(self):
        update = _make_update(text="Hi")
        await AccessControlMiddleware._send_private_message(update, "ru")
        update.message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_callback_answer(self):
        update = _make_update(is_callback=True)
        await AccessControlMiddleware._send_private_message(update, "en")
        update.callback_query.answer.assert_called_once()


class TestSendError:
    @pytest.mark.asyncio
    async def test_message_error(self):
        update = _make_update(text="Hi")
        await AccessControlMiddleware._send_error(update, "ru")
        update.message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_callback_error(self):
        update = _make_update(is_callback=True)
        await AccessControlMiddleware._send_error(update, "en")
        update.callback_query.answer.assert_called_once()
