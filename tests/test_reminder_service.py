"""Тесты сервиса напоминаний — format_reminder_message, константы, CRUD."""

import sys
import uuid
from datetime import date, datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Очистка моков из test_events_api.py
for _key in list(sys.modules):
    if _key.startswith("app.services.") or _key == "app.services":
        _mod = sys.modules[_key]
        if hasattr(_mod, "_mock_name"):
            del sys.modules[_key]
for _key in list(sys.modules):
    if _key == "app.db.models" or _key.startswith("app.db."):
        _mod = sys.modules[_key]
        if hasattr(_mod, "_mock_name"):
            del sys.modules[_key]
for _key in ["app.config", "app.db.engine"]:
    if _key in sys.modules and hasattr(sys.modules[_key], "_mock_name"):
        del sys.modules[_key]

from app.services.reminder_service import (  # noqa: E402
    OFFSETS,
    VALID_KEYS,
    create_reminders_for_event,
    recreate_reminders_for_event,
    get_due_reminders,
    mark_sent,
    format_reminder_message,
)


class TestOffsets:
    def test_all_keys_present(self):
        assert set(OFFSETS.keys()) == {"1d", "2h", "1h", "30m", "15m", "0m"}

    def test_valid_keys(self):
        assert VALID_KEYS == {"1d", "2h", "1h", "30m", "15m", "0m"}

    def test_1d_offset(self):
        assert OFFSETS["1d"].total_seconds() == 86400

    def test_2h_offset(self):
        assert OFFSETS["2h"].total_seconds() == 7200

    def test_0m_offset(self):
        assert OFFSETS["0m"].total_seconds() == 0


class TestFormatReminderMessage:
    """Тесты format_reminder_message — чистая функция."""

    def test_basic_ru_with_time(self):
        msg = format_reminder_message(
            "Ужин", date(2026, 4, 1), time(19, 0), "Семья", "2h", lang="ru",
        )
        assert isinstance(msg, str)
        assert "Ужин" in msg
        assert "19:00" in msg
        assert "Семья" in msg

    def test_basic_en_with_time(self):
        msg = format_reminder_message(
            "Dinner", date(2026, 4, 1), time(19, 0), "Family", "2h", lang="en",
        )
        assert isinstance(msg, str)
        assert "Dinner" in msg
        assert "19:00" in msg
        assert "Family" in msg

    def test_without_time_ru(self):
        msg = format_reminder_message(
            "Поездка", date(2026, 4, 1), None, "Семья", "1d", lang="ru",
        )
        assert isinstance(msg, str)
        assert "Поездка" in msg
        assert "Семья" in msg

    def test_without_time_en(self):
        msg = format_reminder_message(
            "Trip", date(2026, 4, 1), None, "Family", "1d", lang="en",
        )
        assert isinstance(msg, str)
        assert "Trip" in msg
        assert "Family" in msg

    def test_reminder_type_1d(self):
        msg = format_reminder_message(
            "Встреча", date(2026, 4, 1), time(10, 0), "Работа", "1d", lang="ru",
        )
        assert "10:00" in msg
        assert "Работа" in msg

    def test_reminder_type_0m(self):
        msg = format_reminder_message(
            "Встреча", date(2026, 4, 1), time(10, 0), "Работа", "0m", lang="ru",
        )
        assert "10:00" in msg

    def test_reminder_type_15m(self):
        msg = format_reminder_message(
            "Ужин", date(2026, 4, 1), time(19, 0), "Семья", "15m", lang="ru",
        )
        assert "19:00" in msg

    def test_reminder_type_30m(self):
        msg = format_reminder_message(
            "Ужин", date(2026, 4, 1), time(19, 0), "Семья", "30m", lang="ru",
        )
        assert "19:00" in msg

    def test_reminder_type_1h(self):
        msg = format_reminder_message(
            "Ужин", date(2026, 4, 1), time(19, 0), "Семья", "1h", lang="ru",
        )
        assert "19:00" in msg

    def test_multiline_output(self):
        msg = format_reminder_message(
            "Ужин", date(2026, 4, 1), time(19, 0), "Семья", "2h", lang="ru",
        )
        lines = msg.strip().split("\n")
        assert len(lines) >= 3

    def test_all_reminder_types_with_time(self):
        """Все типы напоминаний с временем генерируют строку."""
        for rtype in ["1d", "2h", "1h", "30m", "15m", "0m"]:
            msg = format_reminder_message(
                "Тест", date(2026, 4, 1), time(12, 0), "Тест", rtype, lang="ru",
            )
            assert isinstance(msg, str)
            assert len(msg) > 10


# ── Async CRUD tests ──

def _make_event(event_time=time(15, 0), event_date=None, event_id=None):
    e = MagicMock()
    e.id = event_id or uuid.uuid4()
    e.event_date = event_date or date(2026, 6, 1)
    e.event_time = event_time
    e.space_id = uuid.uuid4()
    return e


def _make_user_row(user_id, settings_dict):
    row = MagicMock()
    row.id = user_id
    row.reminder_settings = settings_dict
    return row


_FAR_FUTURE = date(2026, 6, 1)
_FIXED_NOW = datetime(2026, 4, 1, 12, 0, tzinfo=__import__("zoneinfo").ZoneInfo("Europe/Moscow"))


class TestCreateRemindersForEvent:
    @pytest.mark.asyncio
    @patch("app.services.reminder_service.datetime")
    async def test_timed_event_creates_reminders(self, mock_dt):
        mock_dt.now.return_value = _FIXED_NOW
        mock_dt.combine = datetime.combine

        session = AsyncMock()
        rows = [_make_user_row(1, {"1h": True, "30m": True})]
        session.execute = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=rows)))

        event = _make_event(event_time=time(15, 0), event_date=_FAR_FUTURE)
        count = await create_reminders_for_event(session, event, event.space_id)
        assert count == 2
        assert session.add.call_count == 2

    @pytest.mark.asyncio
    @patch("app.services.reminder_service.datetime")
    async def test_allday_event_creates_1d_only(self, mock_dt):
        mock_dt.now.return_value = _FIXED_NOW
        mock_dt.combine = datetime.combine

        session = AsyncMock()
        rows = [_make_user_row(1, {"1d": True, "1h": True})]
        session.execute = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=rows)))

        event = _make_event(event_time=None, event_date=_FAR_FUTURE)
        count = await create_reminders_for_event(session, event, event.space_id)
        assert count == 1

    @pytest.mark.asyncio
    @patch("app.services.reminder_service.datetime")
    async def test_past_remind_at_skipped(self, mock_dt):
        mock_dt.now.return_value = _FIXED_NOW
        mock_dt.combine = datetime.combine

        session = AsyncMock()
        rows = [_make_user_row(1, {"1h": True})]
        session.execute = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=rows)))

        event = _make_event(event_time=time(12, 30), event_date=date(2026, 4, 1))
        count = await create_reminders_for_event(session, event, event.space_id)
        assert count == 0

    @pytest.mark.asyncio
    @patch("app.services.reminder_service.datetime")
    async def test_no_settings_creates_nothing(self, mock_dt):
        mock_dt.now.return_value = _FIXED_NOW
        mock_dt.combine = datetime.combine

        session = AsyncMock()
        rows = [_make_user_row(1, {})]
        session.execute = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=rows)))

        event = _make_event(event_time=time(15, 0), event_date=_FAR_FUTURE)
        count = await create_reminders_for_event(session, event, event.space_id)
        assert count == 0


class TestRecreateReminders:
    @pytest.mark.asyncio
    @patch("app.services.reminder_service.create_reminders_for_event", new_callable=AsyncMock)
    async def test_deletes_and_recreates(self, mock_create):
        mock_create.return_value = 3
        session = AsyncMock()
        event = _make_event()
        space_id = uuid.uuid4()

        count = await recreate_reminders_for_event(session, event, space_id)
        assert count == 3
        session.execute.assert_awaited_once()
        mock_create.assert_awaited_once_with(session, event, space_id)


class TestGetDueReminders:
    @pytest.mark.asyncio
    async def test_returns_results(self):
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = [("r1",), ("r2",)]
        session.execute = AsyncMock(return_value=mock_result)

        result = await get_due_reminders(session)
        assert len(result) == 2


class TestMarkSent:
    @pytest.mark.asyncio
    async def test_marks_existing(self):
        session = AsyncMock()
        reminder = MagicMock()
        reminder.sent = False
        session.get = AsyncMock(return_value=reminder)

        await mark_sent(session, uuid.uuid4())
        assert reminder.sent is True

    @pytest.mark.asyncio
    async def test_noop_for_missing(self):
        session = AsyncMock()
        session.get = AsyncMock(return_value=None)

        await mark_sent(session, uuid.uuid4())
