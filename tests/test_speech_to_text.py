"""Тесты speech_to_text — классы ошибок и edge cases."""

import sys

# Очистка моков
for _key in list(sys.modules):
    if _key.startswith("app.services.") or _key == "app.services":
        _mod = sys.modules[_key]
        if hasattr(_mod, "_mock_name"):
            del sys.modules[_key]

from app.services.speech_to_text import (  # noqa: E402
    TranscriptionError,
    _RetryableError,
    _ClientError,
)


class TestTranscriptionError:
    def test_error_type(self):
        err = TranscriptionError("timeout", "Таймаут")
        assert err.error_type == "timeout"
        assert str(err) == "Таймаут"

    def test_service_disabled(self):
        err = TranscriptionError("service_disabled", "No key")
        assert err.error_type == "service_disabled"

    def test_auth_error(self):
        err = TranscriptionError("auth_error", "401")
        assert err.error_type == "auth_error"

    def test_empty_result(self):
        err = TranscriptionError("empty_result", "No text")
        assert err.error_type == "empty_result"

    def test_bad_request(self):
        err = TranscriptionError("bad_request", "400")
        assert err.error_type == "bad_request"

    def test_service_unavailable(self):
        err = TranscriptionError("service_unavailable", "Unavailable")
        assert err.error_type == "service_unavailable"


class TestRetryableError:
    def test_attributes(self):
        err = _RetryableError(500, "Internal Server Error")
        assert err.status == 500
        assert err.body == "Internal Server Error"

    def test_429(self):
        err = _RetryableError(429, "Too Many Requests")
        assert err.status == 429


class TestClientError:
    def test_attributes(self):
        err = _ClientError(400, "Bad Request")
        assert err.status == 400
        assert err.body == "Bad Request"

    def test_401(self):
        err = _ClientError(401, "Unauthorized")
        assert err.status == 401
