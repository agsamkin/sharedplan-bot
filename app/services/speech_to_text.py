import asyncio
import logging
import time as time_module

import aiohttp

from app.config import settings

logger = logging.getLogger(__name__)

_NEXARA_URL = "https://api.nexara.ru/api/v1/audio/transcriptions"
_TIMEOUT_SECONDS = 30
_MAX_RETRIES = 2
_BACKOFF_BASE = 2  # seconds


class TranscriptionError(Exception):
    def __init__(self, error_type: str, message: str) -> None:
        self.error_type = error_type
        super().__init__(message)


async def transcribe(audio_bytes: bytes) -> str:
    """Транскрипция аудио через Nexara API."""
    last_error: Exception | None = None

    for attempt in range(_MAX_RETRIES):
        start = time_module.monotonic()
        try:
            result = await _send_request(audio_bytes)
            duration_ms = int((time_module.monotonic() - start) * 1000)

            text = result.get("text", "").strip()
            if not text:
                logger.warning(
                    "Nexara empty result: duration_ms=%d audio_size_bytes=%d",
                    duration_ms, len(audio_bytes),
                )
                raise TranscriptionError("empty_result", "Пустой результат транскрипции")

            logger.info(
                "Nexara transcription: duration_ms=%d audio_size_bytes=%d transcription_length=%d",
                duration_ms, len(audio_bytes), len(text),
            )
            return text

        except TranscriptionError:
            raise

        except aiohttp.ServerTimeoutError as e:
            duration_ms = int((time_module.monotonic() - start) * 1000)
            logger.warning(
                "Nexara timeout: duration_ms=%d audio_size_bytes=%d attempt=%d/%d",
                duration_ms, len(audio_bytes), attempt + 1, _MAX_RETRIES,
            )
            last_error = e

        except _RetryableError as e:
            duration_ms = int((time_module.monotonic() - start) * 1000)
            logger.warning(
                "Nexara server error: http_status=%d duration_ms=%d audio_size_bytes=%d attempt=%d/%d",
                e.status, duration_ms, len(audio_bytes), attempt + 1, _MAX_RETRIES,
            )
            last_error = e

        except _ClientError as e:
            duration_ms = int((time_module.monotonic() - start) * 1000)
            logger.error(
                "Nexara client error: http_status=%d duration_ms=%d audio_size_bytes=%d error_body=%s",
                e.status, duration_ms, len(audio_bytes), e.body,
            )
            if e.status == 401:
                raise TranscriptionError("auth_error", "Ошибка авторизации Nexara") from e
            raise TranscriptionError("bad_request", f"Ошибка запроса: HTTP {e.status}") from e

        except aiohttp.ClientError as e:
            duration_ms = int((time_module.monotonic() - start) * 1000)
            logger.warning(
                "Nexara connection error: duration_ms=%d audio_size_bytes=%d attempt=%d/%d",
                duration_ms, len(audio_bytes), attempt + 1, _MAX_RETRIES,
            )
            last_error = e

        if attempt < _MAX_RETRIES - 1:
            await asyncio.sleep(_BACKOFF_BASE * (2 ** attempt))

    if isinstance(last_error, aiohttp.ServerTimeoutError):
        raise TranscriptionError("timeout", "Таймаут запроса к Nexara") from last_error
    raise TranscriptionError("service_unavailable", "Nexara недоступен") from last_error


class _RetryableError(Exception):
    def __init__(self, status: int, body: str) -> None:
        self.status = status
        self.body = body


class _ClientError(Exception):
    def __init__(self, status: int, body: str) -> None:
        self.status = status
        self.body = body


async def _send_request(audio_bytes: bytes) -> dict:
    """Отправка multipart-запроса в Nexara API."""
    timeout = aiohttp.ClientTimeout(total=_TIMEOUT_SECONDS)
    headers = {"Authorization": f"Bearer {settings.NEXARA_API_KEY}"}

    form = aiohttp.FormData()
    form.add_field("file", audio_bytes, filename="voice.ogg", content_type="audio/ogg")
    form.add_field("response_format", "json")

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(_NEXARA_URL, headers=headers, data=form) as resp:
            body = await resp.text()
            if resp.status >= 500:
                raise _RetryableError(resp.status, body)
            if resp.status == 429:
                raise _RetryableError(resp.status, body)
            if resp.status >= 400:
                raise _ClientError(resp.status, body)
            return await resp.json(content_type=None)
