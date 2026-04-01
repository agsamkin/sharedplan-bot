"""Тесты callback-обработчиков."""

import sys
from datetime import date, time
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

from app.bot.callbacks.event_confirm import (  # noqa: E402
    on_event_confirm,
    on_event_cancel,
    on_event_edit,
    handle_event_edit,
    on_event_past_confirm,
    on_event_past_cancel,
)
from app.bot.callbacks.space_select import on_space_select  # noqa: E402
from app.services.llm_parser import ParseError  # noqa: E402


def _make_callback(user_id=100, data="event_confirm"):
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = user_id
    cb.from_user.first_name = "Иван"
    cb.data = data
    cb.message = MagicMock()
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb


def _make_state(data=None):
    state = AsyncMock()
    state.get_data = AsyncMock(return_value=data or {})
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    return state


class TestOnEventCancel:
    @pytest.mark.asyncio
    async def test_cancels_and_clears(self):
        cb = _make_callback()
        state = _make_state()
        await on_event_cancel(cb, state, lang="ru")
        cb.message.edit_text.assert_called_once()
        state.clear.assert_called_once()
        cb.answer.assert_called_once()


class TestOnEventEdit:
    @pytest.mark.asyncio
    async def test_sets_edit_state(self):
        cb = _make_callback(data="event_edit")
        state = _make_state()
        await on_event_edit(cb, state, lang="ru")
        state.set_state.assert_called_once()
        cb.message.edit_text.assert_called_once()
        cb.answer.assert_called_once()


class TestOnEventPastCancel:
    @pytest.mark.asyncio
    async def test_cancels_and_clears(self):
        cb = _make_callback(data="event_past_cancel")
        state = _make_state()
        await on_event_past_cancel(cb, state, lang="ru")
        cb.message.edit_text.assert_called_once()
        state.clear.assert_called_once()
        cb.answer.assert_called_once()


class TestOnEventConfirm:
    @pytest.mark.asyncio
    async def test_no_data_answers_error(self):
        cb = _make_callback()
        state = _make_state(data={})
        session = AsyncMock()
        bot = AsyncMock()
        await on_event_confirm(cb, state, session, bot, lang="ru")
        cb.answer.assert_called()

    @pytest.mark.asyncio
    async def test_creates_event_and_notifies(self):
        space_id = uuid4()
        state_data = {
            "parsed_title": "Ужин",
            "parsed_date": "2026-04-10",
            "parsed_time": "19:00",
            "space_id": str(space_id),
            "raw_input": "Ужин завтра",
            "lang": "ru",
        }
        cb = _make_callback(user_id=100)
        state = _make_state(data=state_data)
        session = AsyncMock()
        bot = AsyncMock()
        bot.send_message = AsyncMock()

        mock_event = MagicMock()
        mock_event.recurrence_rule = None

        mock_space = MagicMock()
        mock_space.name = "Семья"

        with patch("app.bot.callbacks.event_confirm.event_service") as mock_es, \
             patch("app.bot.callbacks.event_confirm.reminder_service") as mock_rs, \
             patch("app.bot.callbacks.event_confirm.space_service") as mock_ss:
            mock_es.create_event = AsyncMock(return_value=mock_event)
            mock_rs.create_reminders_for_event = AsyncMock(return_value=3)
            mock_ss.get_space_by_id = AsyncMock(return_value=mock_space)
            mock_ss.get_space_members = AsyncMock(return_value=[
                {"user_id": 100, "first_name": "Иван"},
                {"user_id": 200, "first_name": "Мария"},
            ])
            await on_event_confirm(cb, state, session, bot, lang="ru")

        mock_es.create_event.assert_called_once()
        state.clear.assert_called_once()
        # Уведомление отправлено участнику 200, не создателю 100
        bot.send_message.assert_called_once()
        assert bot.send_message.call_args[0][0] == 200


class TestOnEventPastConfirm:
    @pytest.mark.asyncio
    async def test_no_data_answers_error(self):
        cb = _make_callback(data="event_past_confirm")
        state = _make_state(data={})
        session = AsyncMock()
        await on_event_past_confirm(cb, state, session, lang="ru")
        cb.answer.assert_called()

    @pytest.mark.asyncio
    async def test_shows_confirmation(self):
        space_id = uuid4()
        state_data = {
            "parsed_title": "Ужин",
            "parsed_date": "2026-04-10",
            "parsed_time": "19:00",
            "space_id": str(space_id),
            "lang": "ru",
        }
        cb = _make_callback(data="event_past_confirm")
        state = _make_state(data=state_data)
        session = AsyncMock()

        with patch("app.bot.callbacks.event_confirm.event_service") as mock_es:
            mock_es.find_conflicting_events = AsyncMock(return_value=[])
            await on_event_past_confirm(cb, state, session, lang="ru")

        state.set_state.assert_called_once()
        cb.message.edit_text.assert_called_once()
        cb.answer.assert_called()


class TestOnEventConfirmWithRecurrence:
    @pytest.mark.asyncio
    async def test_creates_recurring_event(self):
        """Повторяющееся событие генерирует вхождения."""
        space_id = uuid4()
        state_data = {
            "parsed_title": "Планёрка",
            "parsed_date": "2026-04-10",
            "parsed_time": "10:00",
            "space_id": str(space_id),
            "raw_input": "Планёрка каждую неделю",
            "recurrence_rule": "weekly",
            "lang": "ru",
        }
        cb = _make_callback(user_id=100)
        state = _make_state(data=state_data)
        session = AsyncMock()
        bot = AsyncMock()
        bot.send_message = AsyncMock()

        mock_event = MagicMock()
        mock_event.recurrence_rule = "weekly"

        mock_space = MagicMock()
        mock_space.name = "Работа"

        with patch("app.bot.callbacks.event_confirm.event_service") as mock_es, \
             patch("app.bot.callbacks.event_confirm.reminder_service") as mock_rs, \
             patch("app.bot.callbacks.event_confirm.space_service") as mock_ss, \
             patch("app.bot.callbacks.event_confirm.recurrence_service", create=True) as mock_rec:
            mock_es.create_event = AsyncMock(return_value=mock_event)
            mock_rs.create_reminders_for_event = AsyncMock(return_value=3)
            mock_ss.get_space_by_id = AsyncMock(return_value=mock_space)
            mock_ss.get_space_members = AsyncMock(return_value=[
                {"user_id": 100, "first_name": "Иван"},
            ])
            with patch("app.services.recurrence_service.generate_occurrences", new_callable=AsyncMock) as mock_gen:
                mock_gen.return_value = 5
                await on_event_confirm(cb, state, session, bot, lang="ru")

        mock_es.create_event.assert_called_once()
        state.clear.assert_called_once()


class TestHandleEventEdit:
    @pytest.mark.asyncio
    async def test_parse_error_stays_in_edit_state(self):
        """Ошибка парсинга — остаёмся в waiting_for_edit."""
        msg = MagicMock()
        msg.text = "что-то непонятное"
        msg.chat = MagicMock()
        msg.chat.id = 100
        msg.answer = AsyncMock()
        state = _make_state(data={"lang": "ru"})
        session = AsyncMock()
        bot = AsyncMock()
        bot.send_chat_action = AsyncMock()

        with patch("app.bot.callbacks.event_confirm.parse_event", new_callable=AsyncMock) as mock_pe:
            mock_pe.side_effect = ParseError("timeout", "Timeout")
            await handle_event_edit(msg, state, session, bot, lang="ru")

        msg.answer.assert_called_once()
        state.set_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_successful_edit(self):
        """Успешный повторный ввод — показывает подтверждение."""
        from app.services.llm_parser import ParsedEvent
        msg = MagicMock()
        msg.text = "Ужин послезавтра в 20:00"
        msg.chat = MagicMock()
        msg.chat.id = 100
        msg.answer = AsyncMock()
        state = _make_state(data={"space_id": str(uuid4()), "lang": "ru"})
        session = AsyncMock()
        bot = AsyncMock()
        bot.send_chat_action = AsyncMock()

        parsed = ParsedEvent.model_validate({
            "title": "Ужин",
            "date": "2026-04-10",
            "time": "20:00",
        })

        with patch("app.bot.callbacks.event_confirm.parse_event", new_callable=AsyncMock) as mock_pe, \
             patch("app.bot.callbacks.event_confirm.event_service") as mock_es:
            mock_pe.return_value = parsed
            mock_es.find_conflicting_events = AsyncMock(return_value=[])
            await handle_event_edit(msg, state, session, bot, lang="ru")

        state.update_data.assert_called()
        state.set_state.assert_called()
        msg.answer.assert_called_once()


class TestOnSpaceSelect:
    @pytest.mark.asyncio
    async def test_invalid_parts_answers_error(self):
        cb = _make_callback(data="space_select:bad")
        state = _make_state()
        session = AsyncMock()
        await on_space_select(cb, session, "botuser", state, lang="ru")
        cb.answer.assert_called()

    @pytest.mark.asyncio
    async def test_event_action_shows_confirmation(self):
        space_id = uuid4()
        state_data = {
            "parsed_title": "Встреча",
            "parsed_date": "2026-04-15",
            "parsed_time": "10:00",
            "lang": "ru",
        }
        cb = _make_callback(data=f"space_select:{space_id}:event")
        state = _make_state(data=state_data)
        session = AsyncMock()

        with patch("app.bot.callbacks.space_select.event_service") as mock_es:
            mock_es.find_conflicting_events = AsyncMock(return_value=[])
            await on_space_select(cb, session, "botuser", state, lang="ru")

        state.update_data.assert_called()
        cb.message.edit_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_unknown_action(self):
        space_id = uuid4()
        state_data = {"lang": "ru"}
        cb = _make_callback(data=f"space_select:{space_id}:unknown")
        state = _make_state(data=state_data)
        session = AsyncMock()
        await on_space_select(cb, session, "botuser", state, lang="ru")
        cb.answer.assert_called()

    @pytest.mark.asyncio
    async def test_event_action_past_date_shows_warning(self):
        """Событие с прошедшей датой — показать предупреждение."""
        space_id = uuid4()
        state_data = {
            "parsed_title": "Встреча",
            "parsed_date": "2020-01-01",
            "parsed_time": "10:00",
            "lang": "ru",
        }
        cb = _make_callback(data=f"space_select:{space_id}:event")
        state = _make_state(data=state_data)
        session = AsyncMock()

        await on_space_select(cb, session, "botuser", state, lang="ru")

        state.update_data.assert_called()
        state.set_state.assert_called()
        cb.message.edit_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_event_action_with_conflicts(self):
        """Событие с конфликтами — показать предупреждение."""
        space_id = uuid4()
        state_data = {
            "parsed_title": "Встреча",
            "parsed_date": "2026-06-15",
            "parsed_time": "14:00",
            "lang": "ru",
        }
        cb = _make_callback(data=f"space_select:{space_id}:event")
        state = _make_state(data=state_data)
        session = AsyncMock()

        conflict = MagicMock()
        conflict.title = "Другое"
        conflict.event_time = time(14, 30)

        with patch("app.bot.callbacks.space_select.event_service") as mock_es:
            mock_es.find_conflicting_events = AsyncMock(return_value=[conflict])
            await on_space_select(cb, session, "botuser", state, lang="ru")

        cb.message.edit_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_event_action_without_time(self):
        """Событие без времени — нет проверки конфликтов."""
        space_id = uuid4()
        state_data = {
            "parsed_title": "Поездка",
            "parsed_date": "2026-06-15",
            "parsed_time": None,
            "lang": "ru",
        }
        cb = _make_callback(data=f"space_select:{space_id}:event")
        state = _make_state(data=state_data)
        session = AsyncMock()

        await on_space_select(cb, session, "botuser", state, lang="ru")
        cb.message.edit_text.assert_called_once()


class TestOnEventConfirmNotificationError:
    @pytest.mark.asyncio
    async def test_notification_error_doesnt_break(self):
        """Ошибка уведомления не ломает ответ."""
        space_id = uuid4()
        state_data = {
            "parsed_title": "Ужин",
            "parsed_date": "2026-04-10",
            "parsed_time": "19:00",
            "space_id": str(space_id),
            "raw_input": "Ужин",
            "lang": "ru",
        }
        cb = _make_callback(user_id=100)
        state = _make_state(data=state_data)
        session = AsyncMock()
        bot = AsyncMock()
        bot.send_message = AsyncMock(side_effect=Exception("Telegram error"))

        mock_event = MagicMock()
        mock_event.recurrence_rule = None

        mock_space = MagicMock()
        mock_space.name = "Семья"

        with patch("app.bot.callbacks.event_confirm.event_service") as mock_es, \
             patch("app.bot.callbacks.event_confirm.reminder_service") as mock_rs, \
             patch("app.bot.callbacks.event_confirm.space_service") as mock_ss:
            mock_es.create_event = AsyncMock(return_value=mock_event)
            mock_rs.create_reminders_for_event = AsyncMock(return_value=3)
            mock_ss.get_space_by_id = AsyncMock(return_value=mock_space)
            mock_ss.get_space_members = AsyncMock(return_value=[
                {"user_id": 100, "first_name": "Иван"},
                {"user_id": 200, "first_name": "Мария"},
            ])
            await on_event_confirm(cb, state, session, bot, lang="ru")

        # Ответ всё равно отправлен
        state.clear.assert_called_once()
        cb.answer.assert_called()
