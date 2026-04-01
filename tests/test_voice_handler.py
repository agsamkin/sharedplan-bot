"""Тесты хендлера голосовых сообщений."""

import sys
from io import BytesIO
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

from app.bot.handlers.voice import (  # noqa: E402
    handle_voice_event,
    MAX_VOICE_DURATION_SECONDS,
    MAX_VOICE_FILE_SIZE_BYTES,
)
from app.services.speech_to_text import TranscriptionError  # noqa: E402
from app.services.llm_parser import ParseError  # noqa: E402


def _make_voice_message(duration=10, file_size=1024):
    msg = MagicMock()
    msg.from_user = MagicMock()
    msg.from_user.id = 100
    msg.chat = MagicMock()
    msg.chat.id = 100
    msg.answer = AsyncMock()
    msg.voice = MagicMock()
    msg.voice.duration = duration
    msg.voice.file_size = file_size
    msg.voice.file_id = "file_123"
    return msg


class TestVoiceConstants:
    def test_max_duration(self):
        assert MAX_VOICE_DURATION_SECONDS == 120

    def test_max_file_size(self):
        assert MAX_VOICE_FILE_SIZE_BYTES == 5 * 1024 * 1024


class TestHandleVoiceEvent:
    @pytest.mark.asyncio
    async def test_too_long_duration(self):
        msg = _make_voice_message(duration=200)
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()

        await handle_voice_event(msg, state, session, bot, lang="ru")
        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_too_large_file(self):
        msg = _make_voice_message(file_size=10 * 1024 * 1024)
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()

        await handle_voice_event(msg, state, session, bot, lang="ru")
        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_transcription_error(self):
        msg = _make_voice_message()
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        file_mock = MagicMock()
        file_mock.file_path = "voice/file.ogg"
        bot.get_file = AsyncMock(return_value=file_mock)
        bot.download_file = AsyncMock()
        bot.send_chat_action = AsyncMock()

        with patch("app.bot.handlers.voice.transcribe", new_callable=AsyncMock) as mock_t:
            mock_t.side_effect = TranscriptionError("timeout", "Timeout")
            await handle_voice_event(msg, state, session, bot, lang="ru")

        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_parse_error_after_transcription(self):
        msg = _make_voice_message()
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        file_mock = MagicMock()
        file_mock.file_path = "voice/file.ogg"
        bot.get_file = AsyncMock(return_value=file_mock)
        bot.download_file = AsyncMock()
        bot.send_chat_action = AsyncMock()

        with patch("app.bot.handlers.voice.transcribe", new_callable=AsyncMock) as mock_t, \
             patch("app.bot.handlers.voice.parse_event", new_callable=AsyncMock) as mock_p, \
             patch("app.bot.handlers.voice.settings") as mock_settings:
            mock_t.return_value = "Ужин завтра"
            mock_p.side_effect = ParseError("timeout", "Timeout")
            mock_settings.MINI_APP_URL = ""
            await handle_voice_event(msg, state, session, bot, lang="ru")

        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_transcript_too_long(self):
        msg = _make_voice_message()
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        file_mock = MagicMock()
        file_mock.file_path = "voice/file.ogg"
        bot.get_file = AsyncMock(return_value=file_mock)
        bot.download_file = AsyncMock()
        bot.send_chat_action = AsyncMock()

        with patch("app.bot.handlers.voice.transcribe", new_callable=AsyncMock) as mock_t:
            mock_t.return_value = "a" * 1500  # Слишком длинный
            await handle_voice_event(msg, state, session, bot, lang="ru")

        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_auth_error_logs_as_error(self):
        msg = _make_voice_message()
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        file_mock = MagicMock()
        file_mock.file_path = "voice/file.ogg"
        bot.get_file = AsyncMock(return_value=file_mock)
        bot.download_file = AsyncMock()
        bot.send_chat_action = AsyncMock()

        with patch("app.bot.handlers.voice.transcribe", new_callable=AsyncMock) as mock_t:
            mock_t.side_effect = TranscriptionError("auth_error", "401")
            await handle_voice_event(msg, state, session, bot, lang="ru")

        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_parse_error_service_disabled_with_url(self):
        """service_disabled + MINI_APP_URL показывает кнопку."""
        msg = _make_voice_message()
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        file_mock = MagicMock()
        file_mock.file_path = "voice/file.ogg"
        bot.get_file = AsyncMock(return_value=file_mock)
        bot.download_file = AsyncMock()
        bot.send_chat_action = AsyncMock()

        with patch("app.bot.handlers.voice.transcribe", new_callable=AsyncMock) as mock_t, \
             patch("app.bot.handlers.voice.parse_event", new_callable=AsyncMock) as mock_p, \
             patch("app.bot.handlers.voice.settings") as mock_settings:
            mock_t.return_value = "Ужин"
            mock_p.side_effect = ParseError("service_disabled", "No key")
            mock_settings.MINI_APP_URL = "https://app.example.com"
            await handle_voice_event(msg, state, session, bot, lang="ru")

        msg.answer.assert_called_once()
        _, kwargs = msg.answer.call_args
        assert "reply_markup" in kwargs
        assert kwargs["reply_markup"] is not None
