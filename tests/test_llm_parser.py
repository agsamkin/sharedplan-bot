"""Тесты LLM-парсера — валидация ответа, ParseError, ParsedEvent."""

import sys
from datetime import date, time
from unittest.mock import patch

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
