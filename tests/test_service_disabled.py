"""Тесты для graceful degradation при отсутствии API-ключей."""

import sys
from unittest.mock import patch

import pytest

# test_events_api.py мокает sys.modules["app.services"] на уровне модуля.
# Восстанавливаем реальный пакет, чтобы импорты подмодулей работали.
for _key in list(sys.modules):
    if _key == "app.services" or _key.startswith("app.services."):
        _mod = sys.modules[_key]
        if hasattr(_mod, "_mock_name"):
            del sys.modules[_key]

from app.services.speech_to_text import TranscriptionError, transcribe  # noqa: E402
from app.services.llm_parser import ParseError, parse_event  # noqa: E402


@pytest.mark.asyncio(loop_scope="session")
async def test_transcribe_raises_service_disabled_without_key():
    """transcribe() выбрасывает TranscriptionError(service_disabled) без NEXARA_API_KEY."""
    with patch("app.services.speech_to_text.settings") as mock_settings:
        mock_settings.NEXARA_API_KEY = None
        with pytest.raises(TranscriptionError) as exc_info:
            await transcribe(b"fake audio")
        assert exc_info.value.error_type == "service_disabled"


@pytest.mark.asyncio(loop_scope="session")
async def test_parse_event_raises_service_disabled_without_key():
    """parse_event() выбрасывает ParseError(service_disabled) без OPENROUTER_API_KEY."""
    with patch("app.services.llm_parser.settings") as mock_settings:
        mock_settings.OPENROUTER_API_KEY = None
        with pytest.raises(ParseError) as exc_info:
            await parse_event("Ужин завтра в 19:00")
        assert exc_info.value.error_type == "service_disabled"
