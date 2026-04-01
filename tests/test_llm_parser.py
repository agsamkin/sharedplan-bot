"""Тесты LLM-парсера — валидация ответа, ParseError, ParsedEvent, _call_llm, parse_event."""

import sys
from datetime import date, datetime, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Очистка моков
for _key in list(sys.modules):
    if _key.startswith("app.services.") or _key == "app.services":
        _mod = sys.modules[_key]
        if hasattr(_mod, "_mock_name"):
            del sys.modules[_key]

from app.services.llm_parser import (  # noqa: E402
    ParsedEvent,
    ParseError,
    _validate_response,
    _now_in_tz,
    _call_llm,
    _get_client,
    parse_event,
)


class TestParsedEventValidation:
    def test_valid_full(self):
        event = ParsedEvent.model_validate({
            "title": "Ужин",
            "date": "2026-04-01",
            "time": "19:00",
        })
        assert event.title == "Ужин"
        assert event.event_date == date(2026, 4, 1)
        assert event.event_time == time(19, 0)

    def test_valid_without_time(self):
        event = ParsedEvent.model_validate({
            "title": "Поездка",
            "date": "2026-04-01",
            "time": None,
        })
        assert event.event_time is None

    def test_date_too_far_in_future(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError, match="далеко в будущем"):
            ParsedEvent.model_validate({
                "title": "Test",
                "date": "2030-01-01",
                "time": None,
            })

    def test_recurrence_rule_valid(self):
        event = ParsedEvent.model_validate({
            "title": "Test",
            "date": "2026-04-01",
            "time": "10:00",
            "recurrence_rule": "weekly",
        })
        assert event.recurrence_rule == "weekly"

    def test_recurrence_rule_invalid(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ParsedEvent.model_validate({
                "title": "Test",
                "date": "2026-04-01",
                "time": "10:00",
                "recurrence_rule": "every_other_day",
            })


class TestValidateResponse:
    def test_valid_json(self):
        raw = '{"title": "Ужин", "date": "2026-04-01", "time": "19:00"}'
        result = _validate_response(raw)
        assert result.title == "Ужин"
        assert result.event_date == date(2026, 4, 1)

    def test_invalid_json(self):
        with pytest.raises(ParseError) as exc_info:
            _validate_response("not json")
        assert exc_info.value.error_type == "invalid_json"

    def test_missing_required_field(self):
        with pytest.raises(ParseError) as exc_info:
            _validate_response('{"title": "Ужин"}')
        assert exc_info.value.error_type == "invalid_json"

    def test_empty_string(self):
        with pytest.raises(ParseError) as exc_info:
            _validate_response("")
        assert exc_info.value.error_type == "invalid_json"


class TestParseError:
    def test_error_type(self):
        err = ParseError("timeout", "Request timed out")
        assert err.error_type == "timeout"
        assert str(err) == "Request timed out"

    def test_service_disabled(self):
        err = ParseError("service_disabled", "No API key")
        assert err.error_type == "service_disabled"

    def test_network_error(self):
        err = ParseError("network", "Connection error")
        assert err.error_type == "network"

    def test_rate_limit(self):
        err = ParseError("rate_limit", "Rate limit exceeded")
        assert err.error_type == "rate_limit"

    def test_invalid_json_error(self):
        err = ParseError("invalid_json", "Bad response")
        assert err.error_type == "invalid_json"


class TestNowInTz:
    def test_returns_datetime(self):
        from datetime import datetime
        result = _now_in_tz()
        assert isinstance(result, datetime)
        assert result.tzinfo is not None


# ── _get_client tests ──


class TestGetClient:
    def test_creates_client(self):
        import app.services.llm_parser as mod
        mod._client = None
        with patch("app.services.llm_parser.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            client = _get_client()
            assert client is not None
            mod._client = None  # cleanup


# ── _call_llm tests ──


class TestCallLlm:
    @pytest.mark.asyncio
    @patch("app.services.llm_parser._get_client")
    async def test_success(self, mock_get_client):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"title":"test"}'))]
        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5)
        mock_response.model = "test-model"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await _call_llm([{"role": "user", "content": "test"}])
        assert result == '{"title":"test"}'

    @pytest.mark.asyncio
    @patch("app.services.llm_parser.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.services.llm_parser._get_client")
    async def test_timeout_retries(self, mock_get_client, mock_sleep):
        from openai import APITimeoutError
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=APITimeoutError(request=MagicMock())
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(ParseError) as exc_info:
            await _call_llm([{"role": "user", "content": "test"}])
        assert exc_info.value.error_type == "timeout"

    @pytest.mark.asyncio
    @patch("app.services.llm_parser.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.services.llm_parser._get_client")
    async def test_rate_limit_429(self, mock_get_client, mock_sleep):
        from openai import APIStatusError
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        err = APIStatusError(message="rate limit", response=mock_resp, body=None)
        mock_client.chat.completions.create = AsyncMock(side_effect=err)
        mock_get_client.return_value = mock_client

        with pytest.raises(ParseError) as exc_info:
            await _call_llm([{"role": "user", "content": "test"}])
        assert exc_info.value.error_type == "rate_limit"

    @pytest.mark.asyncio
    @patch("app.services.llm_parser._get_client")
    async def test_api_status_error_non_retryable(self, mock_get_client):
        from openai import APIStatusError
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        err = APIStatusError(message="forbidden", response=mock_resp, body=None)
        mock_client.chat.completions.create = AsyncMock(side_effect=err)
        mock_get_client.return_value = mock_client

        with pytest.raises(ParseError) as exc_info:
            await _call_llm([{"role": "user", "content": "test"}])
        assert exc_info.value.error_type == "network"

    @pytest.mark.asyncio
    @patch("app.services.llm_parser.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.services.llm_parser._get_client")
    async def test_connection_error_retries(self, mock_get_client, mock_sleep):
        from openai import APIConnectionError
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=APIConnectionError(request=MagicMock())
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(ParseError) as exc_info:
            await _call_llm([{"role": "user", "content": "test"}])
        assert exc_info.value.error_type == "network"

    @pytest.mark.asyncio
    @patch("app.services.llm_parser.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.services.llm_parser._get_client")
    async def test_500_retries(self, mock_get_client, mock_sleep):
        from openai import APIStatusError
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        err = APIStatusError(message="server error", response=mock_resp, body=None)
        mock_client.chat.completions.create = AsyncMock(side_effect=err)
        mock_get_client.return_value = mock_client

        with pytest.raises(ParseError) as exc_info:
            await _call_llm([{"role": "user", "content": "test"}])
        assert exc_info.value.error_type == "network"


# ── parse_event tests ──


class TestParseEvent:
    @pytest.mark.asyncio
    @patch("app.services.llm_parser.settings")
    async def test_service_disabled(self, mock_settings):
        mock_settings.OPENROUTER_API_KEY = None
        with pytest.raises(ParseError) as exc_info:
            await parse_event("завтра ужин")
        assert exc_info.value.error_type == "service_disabled"

    @pytest.mark.asyncio
    @patch("app.services.llm_parser._call_llm", new_callable=AsyncMock)
    @patch("app.services.llm_parser._now_in_tz")
    @patch("app.services.llm_parser.settings")
    async def test_success(self, mock_settings, mock_now, mock_call):
        mock_settings.OPENROUTER_API_KEY = "key"
        mock_now.return_value = datetime(2026, 4, 1, 12, 0, tzinfo=__import__("zoneinfo").ZoneInfo("Europe/Moscow"))
        mock_call.return_value = '{"title": "Ужин", "date": "2026-04-02", "time": "19:00"}'

        result = await parse_event("завтра ужин в 19")
        assert result.title == "Ужин"
        assert result.event_date == date(2026, 4, 2)

    @pytest.mark.asyncio
    @patch("app.services.llm_parser._call_llm", new_callable=AsyncMock)
    @patch("app.services.llm_parser._now_in_tz")
    @patch("app.services.llm_parser.settings")
    async def test_retry_with_reinforced_prompt(self, mock_settings, mock_now, mock_call):
        mock_settings.OPENROUTER_API_KEY = "key"
        mock_now.return_value = datetime(2026, 4, 1, 12, 0, tzinfo=__import__("zoneinfo").ZoneInfo("Europe/Moscow"))
        # First call returns invalid, second returns valid
        mock_call.side_effect = [
            "invalid json",
            '{"title": "Ужин", "date": "2026-04-02", "time": "19:00"}',
        ]

        result = await parse_event("завтра ужин в 19")
        assert result.title == "Ужин"
        assert mock_call.await_count == 2
