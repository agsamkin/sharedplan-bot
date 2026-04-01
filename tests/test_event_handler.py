"""Тесты хендлера событий — _is_event_in_past и process_parsed_event."""

import sys
from datetime import date, datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

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

from app.bot.handlers.event import (  # noqa: E402
    _is_event_in_past,
    _show_confirmation_or_past_warning,
    handle_text_event,
    process_parsed_event,
    MAX_EVENT_TEXT_LENGTH,
)
from app.services.llm_parser import ParsedEvent, ParseError  # noqa: E402


class TestIsEventInPast:
    def test_past_date(self):
        assert _is_event_in_past(date(2020, 1, 1)) is True

    def test_future_date(self):
        assert _is_event_in_past(date(2027, 6, 1)) is False

    def test_today_no_time(self):
        today = date.today()
        assert _is_event_in_past(today) is False

    def test_today_future_time(self):
        today = date.today()
        future_time = time(23, 59)
        assert _is_event_in_past(today, future_time) is False

    def test_today_past_time(self):
        today = date.today()
        past_time = time(0, 0, 1)
        assert _is_event_in_past(today, past_time) is True

    def test_yesterday(self):
        yesterday = date.today() - timedelta(days=1)
        assert _is_event_in_past(yesterday) is True


class TestMaxEventTextLength:
    def test_value(self):
        assert MAX_EVENT_TEXT_LENGTH == 1000


class TestProcessParsedEvent:
    def _make_parsed(self, title="Ужин", event_date=None, event_time=None, recurrence_rule=None):
        return ParsedEvent.model_validate({
            "title": title,
            "date": (event_date or date(2026, 4, 10)).isoformat(),
            "time": event_time.strftime("%H:%M") if event_time else None,
            "recurrence_rule": recurrence_rule,
        })

    @pytest.mark.asyncio
    async def test_no_spaces_sends_message(self):
        """Если у пользователя нет пространств — отправляется сообщение."""
        message = MagicMock()
        message.from_user = MagicMock()
        message.from_user.id = 100
        message.answer = AsyncMock()

        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        parsed = self._make_parsed()

        with patch("app.bot.handlers.event.space_service") as mock_ss:
            mock_ss.get_user_spaces = AsyncMock(return_value=[])
            await process_parsed_event(
                message, state, session, bot, parsed, raw_input="Ужин", lang="ru",
            )

        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_single_space_shows_confirmation(self):
        """Если одно пространство — показываем карточку подтверждения."""
        message = MagicMock()
        message.from_user = MagicMock()
        message.from_user.id = 100
        message.answer = AsyncMock()

        state = AsyncMock()
        state.get_data = AsyncMock(return_value={})
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        space_id = uuid4()
        parsed = self._make_parsed()

        with patch("app.bot.handlers.event.space_service") as mock_ss:
            mock_ss.get_user_spaces = AsyncMock(return_value=[
                {"id": space_id, "name": "Семья", "role": "admin", "member_count": 1}
            ])
            with patch("app.bot.handlers.event.event_service") as mock_es:
                mock_es.find_conflicting_events = AsyncMock(return_value=[])
                await process_parsed_event(
                    message, state, session, bot, parsed, raw_input="Ужин", lang="ru",
                )

        state.update_data.assert_called()
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_spaces_shows_select(self):
        """Если несколько пространств — показываем выбор."""
        message = MagicMock()
        message.from_user = MagicMock()
        message.from_user.id = 100
        message.answer = AsyncMock()

        state = AsyncMock()
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        parsed = self._make_parsed()

        with patch("app.bot.handlers.event.space_service") as mock_ss:
            mock_ss.get_user_spaces = AsyncMock(return_value=[
                {"id": uuid4(), "name": "Семья", "role": "admin", "member_count": 2},
                {"id": uuid4(), "name": "Работа", "role": "member", "member_count": 5},
            ])
            await process_parsed_event(
                message, state, session, bot, parsed, raw_input="Ужин", lang="ru",
            )

        state.set_state.assert_called_once()
        message.answer.assert_called_once()
        # Проверяем что клавиатура выбора пространства была передана
        _, kwargs = message.answer.call_args
        assert "reply_markup" in kwargs


class TestShowConfirmationOrPastWarning:
    def _make_parsed(self, event_date=None, event_time=None):
        return ParsedEvent.model_validate({
            "title": "Тест",
            "date": (event_date or date(2026, 4, 10)).isoformat(),
            "time": event_time.strftime("%H:%M") if event_time else None,
        })

    @pytest.mark.asyncio
    async def test_past_event_shows_warning(self):
        """Прошедшее событие — показать предупреждение."""
        msg = MagicMock()
        msg.answer = AsyncMock()
        state = AsyncMock()
        state.set_state = AsyncMock()
        session = AsyncMock()
        parsed = self._make_parsed(event_date=date(2020, 1, 1))

        await _show_confirmation_or_past_warning(
            msg, state, session, str(uuid4()), parsed, lang="ru",
        )
        state.set_state.assert_called_once()
        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_future_event_shows_confirmation(self):
        """Будущее событие — показать карточку подтверждения."""
        msg = MagicMock()
        msg.answer = AsyncMock()
        state = AsyncMock()
        state.set_state = AsyncMock()
        session = AsyncMock()
        parsed = self._make_parsed(event_date=date(2027, 6, 1), event_time=time(12, 0))

        with patch("app.bot.handlers.event.event_service") as mock_es:
            mock_es.find_conflicting_events = AsyncMock(return_value=[])
            await _show_confirmation_or_past_warning(
                msg, state, session, str(uuid4()), parsed, lang="ru",
            )

        state.set_state.assert_called_once()
        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_future_event_with_conflicts(self):
        """Будущее событие с конфликтами — добавляет предупреждение."""
        msg = MagicMock()
        msg.answer = AsyncMock()
        state = AsyncMock()
        state.set_state = AsyncMock()
        session = AsyncMock()
        parsed = self._make_parsed(event_date=date(2027, 6, 1), event_time=time(12, 0))

        conflict = MagicMock()
        conflict.title = "Другое событие"
        conflict.event_time = time(12, 30)

        with patch("app.bot.handlers.event.event_service") as mock_es:
            mock_es.find_conflicting_events = AsyncMock(return_value=[conflict])
            await _show_confirmation_or_past_warning(
                msg, state, session, str(uuid4()), parsed, lang="ru",
            )

        msg.answer.assert_called_once()


class TestHandleTextEvent:
    @pytest.mark.asyncio
    async def test_empty_text_ignored(self):
        msg = MagicMock()
        msg.text = ""
        msg.answer = AsyncMock()
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        await handle_text_event(msg, state, session, bot, lang="ru")
        msg.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_too_long_text(self):
        msg = MagicMock()
        msg.text = "a" * 1500
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.answer = AsyncMock()
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        await handle_text_event(msg, state, session, bot, lang="ru")
        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_parse_error(self):
        msg = MagicMock()
        msg.text = "Ужин завтра"
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.chat = MagicMock()
        msg.chat.id = 100
        msg.answer = AsyncMock()
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        bot.send_chat_action = AsyncMock()

        with patch("app.bot.handlers.event.parse_event", new_callable=AsyncMock) as mock_pe, \
             patch("app.bot.handlers.event.settings") as mock_settings:
            mock_pe.side_effect = ParseError("timeout", "Timeout")
            mock_settings.MINI_APP_URL = ""
            await handle_text_event(msg, state, session, bot, lang="ru")

        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_parse_error_service_disabled_with_url(self):
        msg = MagicMock()
        msg.text = "Ужин завтра"
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.chat = MagicMock()
        msg.chat.id = 100
        msg.answer = AsyncMock()
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        bot.send_chat_action = AsyncMock()

        with patch("app.bot.handlers.event.parse_event", new_callable=AsyncMock) as mock_pe, \
             patch("app.bot.handlers.event.settings") as mock_settings:
            mock_pe.side_effect = ParseError("service_disabled", "No key")
            mock_settings.MINI_APP_URL = "https://app.example.com"
            await handle_text_event(msg, state, session, bot, lang="ru")

        msg.answer.assert_called_once()
        _, kwargs = msg.answer.call_args
        assert kwargs.get("reply_markup") is not None

    @pytest.mark.asyncio
    async def test_none_text_ignored(self):
        msg = MagicMock()
        msg.text = None
        msg.answer = AsyncMock()
        state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        await handle_text_event(msg, state, session, bot, lang="ru")
        msg.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_successful_parse(self):
        msg = MagicMock()
        msg.text = "Ужин завтра в 19:00"
        msg.from_user = MagicMock()
        msg.from_user.id = 100
        msg.chat = MagicMock()
        msg.chat.id = 100
        msg.answer = AsyncMock()
        state = AsyncMock()
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        session = AsyncMock()
        bot = AsyncMock()
        bot.send_chat_action = AsyncMock()

        parsed = ParsedEvent.model_validate({
            "title": "Ужин",
            "date": "2026-04-10",
            "time": "19:00",
        })

        with patch("app.bot.handlers.event.parse_event", new_callable=AsyncMock) as mock_pe, \
             patch("app.bot.handlers.event.space_service") as mock_ss, \
             patch("app.bot.handlers.event.event_service") as mock_es:
            mock_pe.return_value = parsed
            mock_ss.get_user_spaces = AsyncMock(return_value=[
                {"id": uuid4(), "name": "Семья", "role": "admin", "member_count": 1}
            ])
            mock_es.find_conflicting_events = AsyncMock(return_value=[])
            await handle_text_event(msg, state, session, bot, lang="ru")

        msg.answer.assert_called_once()
