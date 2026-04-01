"""Тесты сервиса напоминаний — format_reminder_message и константы."""

import sys
from datetime import date, time

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
