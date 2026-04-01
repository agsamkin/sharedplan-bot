"""Тесты speech_to_text — классы ошибок, transcribe, _send_request."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

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
    transcribe,
    _send_request,
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


# ── transcribe function tests ──


class TestTranscribe:
    @pytest.mark.asyncio
    @patch("app.services.speech_to_text.settings")
    async def test_service_disabled(self, mock_settings):
        mock_settings.NEXARA_API_KEY = None
        with pytest.raises(TranscriptionError) as exc_info:
            await transcribe(b"audio")
        assert exc_info.value.error_type == "service_disabled"

    @pytest.mark.asyncio
    @patch("app.services.speech_to_text._send_request", new_callable=AsyncMock)
    @patch("app.services.speech_to_text.settings")
    async def test_success(self, mock_settings, mock_send):
        mock_settings.NEXARA_API_KEY = "key"
        mock_send.return_value = {"text": "привет мир"}

        result = await transcribe(b"audio")
        assert result == "привет мир"

    @pytest.mark.asyncio
    @patch("app.services.speech_to_text._send_request", new_callable=AsyncMock)
    @patch("app.services.speech_to_text.settings")
    async def test_empty_result(self, mock_settings, mock_send):
        mock_settings.NEXARA_API_KEY = "key"
        mock_send.return_value = {"text": "  "}

        with pytest.raises(TranscriptionError) as exc_info:
            await transcribe(b"audio")
        assert exc_info.value.error_type == "empty_result"

    @pytest.mark.asyncio
    @patch("app.services.speech_to_text.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.services.speech_to_text._send_request", new_callable=AsyncMock)
    @patch("app.services.speech_to_text.settings")
    async def test_timeout_retries_then_fails(self, mock_settings, mock_send, mock_sleep):
        mock_settings.NEXARA_API_KEY = "key"
        mock_send.side_effect = aiohttp.ServerTimeoutError()

        with pytest.raises(TranscriptionError) as exc_info:
            await transcribe(b"audio")
        assert exc_info.value.error_type == "timeout"

    @pytest.mark.asyncio
    @patch("app.services.speech_to_text.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.services.speech_to_text._send_request", new_callable=AsyncMock)
    @patch("app.services.speech_to_text.settings")
    async def test_retryable_error_then_success(self, mock_settings, mock_send, mock_sleep):
        mock_settings.NEXARA_API_KEY = "key"
        mock_send.side_effect = [
            _RetryableError(500, "error"),
            {"text": "ok"},
        ]

        result = await transcribe(b"audio")
        assert result == "ok"

    @pytest.mark.asyncio
    @patch("app.services.speech_to_text._send_request", new_callable=AsyncMock)
    @patch("app.services.speech_to_text.settings")
    async def test_client_error_401(self, mock_settings, mock_send):
        mock_settings.NEXARA_API_KEY = "key"
        mock_send.side_effect = _ClientError(401, "Unauthorized")

        with pytest.raises(TranscriptionError) as exc_info:
            await transcribe(b"audio")
        assert exc_info.value.error_type == "auth_error"

    @pytest.mark.asyncio
    @patch("app.services.speech_to_text._send_request", new_callable=AsyncMock)
    @patch("app.services.speech_to_text.settings")
    async def test_client_error_400(self, mock_settings, mock_send):
        mock_settings.NEXARA_API_KEY = "key"
        mock_send.side_effect = _ClientError(400, "Bad Request")

        with pytest.raises(TranscriptionError) as exc_info:
            await transcribe(b"audio")
        assert exc_info.value.error_type == "bad_request"

    @pytest.mark.asyncio
    @patch("app.services.speech_to_text.asyncio.sleep", new_callable=AsyncMock)
    @patch("app.services.speech_to_text._send_request", new_callable=AsyncMock)
    @patch("app.services.speech_to_text.settings")
    async def test_connection_error_retries(self, mock_settings, mock_send, mock_sleep):
        mock_settings.NEXARA_API_KEY = "key"
        mock_send.side_effect = aiohttp.ClientConnectionError()

        with pytest.raises(TranscriptionError) as exc_info:
            await transcribe(b"audio")
        assert exc_info.value.error_type == "service_unavailable"


# ── _send_request tests ──


class TestSendRequest:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"text": "hello"})

        mock_session_ctx = AsyncMock()
        mock_post_ctx = AsyncMock()
        mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_post_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_session_ctx.post = MagicMock(return_value=mock_post_ctx)

        mock_session_factory = AsyncMock()
        mock_session_factory.__aenter__ = AsyncMock(return_value=mock_session_ctx)
        mock_session_factory.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.speech_to_text.aiohttp.ClientSession", return_value=mock_session_factory):
            with patch("app.services.speech_to_text.settings") as mock_settings:
                mock_settings.NEXARA_API_KEY = "key"
                result = await _send_request(b"audio")
                assert result == {"text": "hello"}

    @pytest.mark.asyncio
    async def test_500_raises_retryable(self):
        mock_resp = AsyncMock()
        mock_resp.status = 500
        mock_resp.text = AsyncMock(return_value="error")

        mock_post_ctx = AsyncMock()
        mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_post_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.post = MagicMock(return_value=mock_post_ctx)

        mock_session_factory = AsyncMock()
        mock_session_factory.__aenter__ = AsyncMock(return_value=mock_session_ctx)
        mock_session_factory.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.speech_to_text.aiohttp.ClientSession", return_value=mock_session_factory):
            with patch("app.services.speech_to_text.settings") as mock_settings:
                mock_settings.NEXARA_API_KEY = "key"
                with pytest.raises(_RetryableError):
                    await _send_request(b"audio")

    @pytest.mark.asyncio
    async def test_429_raises_retryable(self):
        mock_resp = AsyncMock()
        mock_resp.status = 429
        mock_resp.text = AsyncMock(return_value="rate limited")

        mock_post_ctx = AsyncMock()
        mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_post_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.post = MagicMock(return_value=mock_post_ctx)

        mock_session_factory = AsyncMock()
        mock_session_factory.__aenter__ = AsyncMock(return_value=mock_session_ctx)
        mock_session_factory.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.speech_to_text.aiohttp.ClientSession", return_value=mock_session_factory):
            with patch("app.services.speech_to_text.settings") as mock_settings:
                mock_settings.NEXARA_API_KEY = "key"
                with pytest.raises(_RetryableError):
                    await _send_request(b"audio")

    @pytest.mark.asyncio
    async def test_400_raises_client_error(self):
        mock_resp = AsyncMock()
        mock_resp.status = 400
        mock_resp.text = AsyncMock(return_value="bad request")

        mock_post_ctx = AsyncMock()
        mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_post_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.post = MagicMock(return_value=mock_post_ctx)

        mock_session_factory = AsyncMock()
        mock_session_factory.__aenter__ = AsyncMock(return_value=mock_session_ctx)
        mock_session_factory.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.speech_to_text.aiohttp.ClientSession", return_value=mock_session_factory):
            with patch("app.services.speech_to_text.settings") as mock_settings:
                mock_settings.NEXARA_API_KEY = "key"
                with pytest.raises(_ClientError):
                    await _send_request(b"audio")
