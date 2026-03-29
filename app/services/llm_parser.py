import asyncio
import logging
import time as time_module
from datetime import date, datetime, time, timezone, timedelta
from typing import Literal, Optional

from openai import AsyncOpenAI, APIStatusError, APITimeoutError, APIConnectionError
from pydantic import BaseModel, Field, ValidationError, field_validator

from app.config import settings
from app.prompts.event_parser import build_messages, build_messages_reinforced

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None
_MAX_RETRIES = 3
_BACKOFF_BASE = 1  # seconds
_MAX_FUTURE_DAYS = 365 * 2  # 2 года


class ParsedEvent(BaseModel):
    title: str
    event_date: date = Field(alias="date")
    event_time: Optional[time] = Field(default=None, alias="time")

    @field_validator("event_date")
    @classmethod
    def date_not_too_far_in_future(cls, v: date) -> date:
        max_date = date.today() + timedelta(days=_MAX_FUTURE_DAYS)
        if v > max_date:
            raise ValueError(f"Дата слишком далеко в будущем (максимум {max_date})")
        return v


class ParseError(Exception):
    def __init__(
        self,
        error_type: Literal["invalid_json", "timeout", "network", "rate_limit", "service_disabled"],
        message: str,
    ) -> None:
        self.error_type = error_type
        super().__init__(message)


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
            timeout=15.0,
        )
    return _client


async def _call_llm(messages: list[dict[str, str]]) -> str:
    """Вызов OpenRouter с retry при 429/5xx."""
    client = _get_client()
    last_error: Exception | None = None

    for attempt in range(_MAX_RETRIES):
        start = time_module.monotonic()
        try:
            response = await client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            duration_ms = int((time_module.monotonic() - start) * 1000)

            usage = response.usage
            logger.info(
                "LLM call: model=%s input_tokens=%s output_tokens=%s duration_ms=%d",
                response.model,
                usage.prompt_tokens if usage else "?",
                usage.completion_tokens if usage else "?",
                duration_ms,
            )

            return response.choices[0].message.content or ""

        except APITimeoutError as e:
            duration_ms = int((time_module.monotonic() - start) * 1000)
            logger.warning(
                "LLM timeout: model=%s duration_ms=%d attempt=%d/%d",
                settings.OPENROUTER_MODEL, duration_ms, attempt + 1, _MAX_RETRIES,
            )
            last_error = e

        except APIStatusError as e:
            duration_ms = int((time_module.monotonic() - start) * 1000)
            logger.warning(
                "LLM error: model=%s status=%d duration_ms=%d attempt=%d/%d",
                settings.OPENROUTER_MODEL, e.status_code, duration_ms,
                attempt + 1, _MAX_RETRIES,
            )
            if e.status_code == 429:
                last_error = e
            elif e.status_code >= 500:
                last_error = e
            else:
                raise ParseError("network", f"API error: {e.status_code}")

        except APIConnectionError as e:
            duration_ms = int((time_module.monotonic() - start) * 1000)
            logger.warning(
                "LLM connection error: model=%s duration_ms=%d attempt=%d/%d",
                settings.OPENROUTER_MODEL, duration_ms, attempt + 1, _MAX_RETRIES,
            )
            last_error = e

        if attempt < _MAX_RETRIES - 1:
            await asyncio.sleep(_BACKOFF_BASE * (2 ** attempt))

    if isinstance(last_error, APIStatusError) and last_error.status_code == 429:
        raise ParseError("rate_limit", "Rate limit exceeded")
    if isinstance(last_error, APITimeoutError):
        raise ParseError("timeout", "Request timed out")
    raise ParseError("network", "Connection error")


def _validate_response(raw: str) -> ParsedEvent:
    """Валидация JSON-ответа LLM через Pydantic."""
    try:
        return ParsedEvent.model_validate_json(raw)
    except (ValidationError, ValueError) as e:
        logger.warning("LLM response validation failed: raw=%r error=%s", raw, e)
        raise ParseError("invalid_json", f"Invalid LLM response: {e}") from e


def _now_in_tz() -> datetime:
    """Текущее время в настроенном часовом поясе."""
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo(settings.TIMEZONE))


async def parse_event(user_text: str) -> ParsedEvent:
    """Парсинг текста пользователя в структурированное событие через LLM."""
    if settings.OPENROUTER_API_KEY is None:
        raise ParseError("service_disabled", "LLM-сервис не настроен: OPENROUTER_API_KEY отсутствует")

    now = _now_in_tz()
    today = now.date()
    current_time = now.time().replace(second=0, microsecond=0)
    messages = build_messages(user_text, today, current_time)

    raw = await _call_llm(messages)

    try:
        return _validate_response(raw)
    except ParseError:
        pass

    # Одна повторная попытка с усиленной инструкцией
    logger.info("LLM returned invalid JSON, retrying with reinforced prompt")
    messages_reinforced = build_messages_reinforced(user_text, today, current_time)
    raw = await _call_llm(messages_reinforced)
    return _validate_response(raw)
