"""Тесты клавиатур, состояний, команд и фильтров бота."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.bot.keyboards.confirm import (
    event_confirm_keyboard,
    event_past_date_keyboard,
    delete_space_confirm_keyboard,
)
from app.bot.keyboards.event_manage import (
    event_manage_keyboard,
    event_delete_confirm_keyboard,
    event_edit_field_keyboard,
    event_edit_time_keyboard,
    event_edit_confirm_keyboard,
)
from app.bot.keyboards.reminder_settings import (
    reminder_settings_keyboard,
    REMINDER_KEYS_ORDER,
)
from app.bot.keyboards.space_select import space_select_keyboard
from app.bot.commands import BOT_COMMANDS
from app.bot.states.create_event import CreateEvent
from app.bot.filters.not_command import NotCommandFilter


# ── Confirm keyboards ──

class TestEventConfirmKeyboard:
    def test_has_three_buttons(self):
        kb = event_confirm_keyboard("ru")
        assert len(kb.inline_keyboard) == 1
        assert len(kb.inline_keyboard[0]) == 3

    def test_callback_data(self):
        kb = event_confirm_keyboard("en")
        data = [b.callback_data for b in kb.inline_keyboard[0]]
        assert "event_confirm" in data
        assert "event_edit" in data
        assert "event_cancel" in data


class TestEventPastDateKeyboard:
    def test_has_two_buttons(self):
        kb = event_past_date_keyboard("ru")
        assert len(kb.inline_keyboard) == 1
        assert len(kb.inline_keyboard[0]) == 2

    def test_callback_data(self):
        kb = event_past_date_keyboard("en")
        data = [b.callback_data for b in kb.inline_keyboard[0]]
        assert "event_past_confirm" in data
        assert "event_past_cancel" in data


class TestDeleteSpaceConfirmKeyboard:
    def test_has_two_buttons(self):
        sid = uuid.uuid4()
        kb = delete_space_confirm_keyboard(sid, "ru")
        assert len(kb.inline_keyboard) == 1
        assert len(kb.inline_keyboard[0]) == 2

    def test_contains_space_id(self):
        sid = uuid.uuid4()
        kb = delete_space_confirm_keyboard(sid, "en")
        data = [b.callback_data for b in kb.inline_keyboard[0]]
        assert any(str(sid) in d for d in data)


# ── Event manage keyboards ──

class TestEventManageKeyboard:
    def test_has_two_buttons(self):
        eid = uuid.uuid4()
        kb = event_manage_keyboard(eid)
        assert len(kb.inline_keyboard) == 1
        assert len(kb.inline_keyboard[0]) == 2

    def test_contains_event_id(self):
        eid = uuid.uuid4()
        kb = event_manage_keyboard(eid)
        data = [b.callback_data for b in kb.inline_keyboard[0]]
        assert all(str(eid) in d for d in data)


class TestEventDeleteConfirmKeyboard:
    def test_has_two_buttons(self):
        eid = uuid.uuid4()
        kb = event_delete_confirm_keyboard(eid)
        assert len(kb.inline_keyboard) == 1
        assert len(kb.inline_keyboard[0]) == 2


class TestEventEditFieldKeyboard:
    def test_has_three_rows(self):
        eid = uuid.uuid4()
        kb = event_edit_field_keyboard(eid)
        assert len(kb.inline_keyboard) == 3


class TestEventEditTimeKeyboard:
    def test_has_one_button(self):
        eid = uuid.uuid4()
        kb = event_edit_time_keyboard(eid)
        assert len(kb.inline_keyboard) == 1
        assert len(kb.inline_keyboard[0]) == 1


class TestEventEditConfirmKeyboard:
    def test_has_two_buttons(self):
        kb = event_edit_confirm_keyboard()
        assert len(kb.inline_keyboard) == 1
        assert len(kb.inline_keyboard[0]) == 2


# ── Reminder settings keyboard ──

class TestReminderSettingsKeyboard:
    def test_six_buttons(self):
        user_settings = {"1d": True, "2h": False, "1h": False, "30m": True, "15m": True, "0m": False}
        kb = reminder_settings_keyboard(user_settings, "ru")
        assert len(kb.inline_keyboard) == 6

    def test_enabled_icon(self):
        user_settings = {"1d": True}
        kb = reminder_settings_keyboard(user_settings, "ru")
        assert "☑" in kb.inline_keyboard[0][0].text

    def test_disabled_icon(self):
        user_settings = {"1d": False}
        kb = reminder_settings_keyboard(user_settings, "ru")
        assert "☐" in kb.inline_keyboard[0][0].text

    def test_callback_data_format(self):
        kb = reminder_settings_keyboard({}, "ru")
        data = kb.inline_keyboard[0][0].callback_data
        assert data.startswith("reminder_toggle:")

    def test_keys_order(self):
        assert REMINDER_KEYS_ORDER == ["1d", "2h", "1h", "30m", "15m", "0m"]


# ── Space select keyboard ──

class TestSpaceSelectKeyboard:
    def test_creates_buttons(self):
        spaces = [
            {"id": uuid.uuid4(), "name": "Семья"},
            {"id": uuid.uuid4(), "name": "Работа"},
        ]
        kb = space_select_keyboard(spaces, "event")
        assert len(kb.inline_keyboard) == 2

    def test_callback_data_format(self):
        sid = uuid.uuid4()
        spaces = [{"id": sid, "name": "Test"}]
        kb = space_select_keyboard(spaces, "event")
        assert kb.inline_keyboard[0][0].callback_data == f"space_select:{sid}:event"

    def test_empty_list(self):
        kb = space_select_keyboard([], "event")
        assert len(kb.inline_keyboard) == 0


# ── Bot commands ──

class TestBotCommands:
    def test_has_commands(self):
        assert len(BOT_COMMANDS) >= 2

    def test_help_command(self):
        commands = {c.command for c in BOT_COMMANDS}
        assert "help" in commands
        assert "privacy" in commands


# ── FSM states ──

class TestCreateEventStates:
    def test_states_exist(self):
        assert CreateEvent.waiting_for_space is not None
        assert CreateEvent.waiting_for_confirm is not None
        assert CreateEvent.waiting_for_edit is not None
        assert CreateEvent.waiting_for_past_confirm is not None


# ── NotCommandFilter ──

class TestNotCommandFilter:
    @pytest.mark.asyncio
    async def test_regular_text_passes(self):
        f = NotCommandFilter()
        msg = MagicMock()
        msg.text = "Ужин завтра в 19:00"
        assert await f(msg) is True

    @pytest.mark.asyncio
    async def test_command_blocked(self):
        f = NotCommandFilter()
        msg = MagicMock()
        msg.text = "/help"
        assert await f(msg) is False

    @pytest.mark.asyncio
    async def test_empty_text_blocked(self):
        f = NotCommandFilter()
        msg = MagicMock()
        msg.text = ""
        assert await f(msg) is False

    @pytest.mark.asyncio
    async def test_none_text_blocked(self):
        f = NotCommandFilter()
        msg = MagicMock()
        msg.text = None
        assert await f(msg) is False
