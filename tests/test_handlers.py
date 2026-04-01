"""Тесты хендлеров /start, /help, /privacy."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

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

from app.bot.handlers.help import cmd_help  # noqa: E402
from app.bot.handlers.privacy import cmd_privacy  # noqa: E402
from app.bot.handlers.start import (  # noqa: E402
    cmd_start,
    cmd_start_join,
    _webapp_keyboard,
    _send_welcome,
    _upsert_user,
)


class TestCmdHelp:
    @pytest.mark.asyncio
    async def test_sends_help_text(self):
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.answer = AsyncMock()
        await cmd_help(msg, lang="ru")
        msg.answer.assert_called_once()
        text = msg.answer.call_args[0][0]
        assert isinstance(text, str)
        assert len(text) > 10

    @pytest.mark.asyncio
    async def test_help_en(self):
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.answer = AsyncMock()
        await cmd_help(msg, lang="en")
        msg.answer.assert_called_once()


class TestCmdPrivacy:
    @pytest.mark.asyncio
    async def test_sends_privacy_text(self):
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.answer = AsyncMock()
        await cmd_privacy(msg, lang="ru")
        msg.answer.assert_called_once()
        text = msg.answer.call_args[0][0]
        assert isinstance(text, str)
        assert len(text) > 10


class TestWebappKeyboard:
    def test_with_url(self):
        with patch("app.bot.handlers.start.settings") as mock_settings:
            mock_settings.MINI_APP_URL = "https://example.com"
            kb = _webapp_keyboard("ru")
        assert len(kb.inline_keyboard) == 1
        assert len(kb.inline_keyboard[0]) == 1

    def test_without_url(self):
        with patch("app.bot.handlers.start.settings") as mock_settings:
            mock_settings.MINI_APP_URL = ""
            kb = _webapp_keyboard("ru")
        assert len(kb.inline_keyboard) == 0


class TestSendWelcome:
    @pytest.mark.asyncio
    async def test_with_spaces(self):
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.answer = AsyncMock()
        session = AsyncMock()

        with patch("app.bot.handlers.start.space_service") as mock_ss:
            mock_ss.get_user_spaces = AsyncMock(return_value=[
                {"id": uuid4(), "name": "Семья", "role": "admin", "member_count": 2},
            ])
            with patch("app.bot.handlers.start.settings") as mock_settings:
                mock_settings.MINI_APP_URL = ""
                await _send_welcome(msg, session, "ru")

        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_without_spaces(self):
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.answer = AsyncMock()
        session = AsyncMock()

        with patch("app.bot.handlers.start.space_service") as mock_ss:
            mock_ss.get_user_spaces = AsyncMock(return_value=[])
            with patch("app.bot.handlers.start.settings") as mock_settings:
                mock_settings.MINI_APP_URL = ""
                await _send_welcome(msg, session, "ru")

        msg.answer.assert_called_once()


class TestCmdStart:
    @pytest.mark.asyncio
    async def test_start_command(self):
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.from_user.username = "testuser"
        msg.from_user.first_name = "Тест"
        msg.from_user.language_code = "ru"
        msg.answer = AsyncMock()
        session = AsyncMock()

        with patch("app.bot.handlers.start.space_service") as mock_ss, \
             patch("app.bot.handlers.start.settings") as mock_settings:
            mock_ss.get_user_spaces = AsyncMock(return_value=[])
            mock_settings.MINI_APP_URL = ""
            await cmd_start(msg, session, lang="ru")

        session.execute.assert_called_once()  # upsert user
        msg.answer.assert_called_once()


class TestCmdStartJoin:
    @pytest.mark.asyncio
    async def test_join_invalid_link(self):
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.from_user.username = "testuser"
        msg.from_user.first_name = "Тест"
        msg.from_user.language_code = "ru"
        msg.answer = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        command = MagicMock()
        command.args = "join_invalid"

        with patch("app.bot.handlers.start.space_service") as mock_ss:
            mock_ss.get_space_by_invite_code = AsyncMock(return_value=None)
            await cmd_start_join(msg, session, command, bot, lang="ru")

        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_join_already_member(self):
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.from_user.username = "testuser"
        msg.from_user.first_name = "Тест"
        msg.from_user.language_code = "ru"
        msg.answer = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        command = MagicMock()
        command.args = "join_abc123"

        mock_space = MagicMock()
        mock_space.name = "Семья"
        mock_space.id = uuid4()

        with patch("app.bot.handlers.start.space_service") as mock_ss:
            mock_ss.get_space_by_invite_code = AsyncMock(return_value=mock_space)
            mock_ss.join_space = AsyncMock(return_value=None)  # уже участник
            await cmd_start_join(msg, session, command, bot, lang="ru")

        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_join_success(self):
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.from_user.username = "testuser"
        msg.from_user.first_name = "Тест"
        msg.from_user.language_code = "ru"
        msg.answer = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        bot.send_message = AsyncMock()
        command = MagicMock()
        command.args = "join_abc123"

        mock_space = MagicMock()
        mock_space.name = "Семья"
        mock_space.id = uuid4()
        mock_membership = MagicMock()

        with patch("app.bot.handlers.start.space_service") as mock_ss:
            mock_ss.get_space_by_invite_code = AsyncMock(return_value=mock_space)
            mock_ss.join_space = AsyncMock(return_value=mock_membership)
            mock_ss.get_space_members = AsyncMock(return_value=[
                {"user_id": 100, "first_name": "Тест"},
                {"user_id": 200, "first_name": "Мария"},
            ])
            await cmd_start_join(msg, session, command, bot, lang="ru")

        msg.answer.assert_called_once()
        bot.send_message.assert_called_once()  # уведомление для user 200

    @pytest.mark.asyncio
    async def test_non_join_deeplink_shows_welcome(self):
        """Deeplink без join_ показывает приветствие."""
        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.from_user.username = "testuser"
        msg.from_user.first_name = "Тест"
        msg.from_user.language_code = "ru"
        msg.answer = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        command = MagicMock()
        command.args = "something_else"

        with patch("app.bot.handlers.start.space_service") as mock_ss, \
             patch("app.bot.handlers.start.settings") as mock_settings:
            mock_ss.get_user_spaces = AsyncMock(return_value=[])
            mock_settings.MINI_APP_URL = ""
            await cmd_start_join(msg, session, command, bot, lang="ru")

        msg.answer.assert_called_once()
