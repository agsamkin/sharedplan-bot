"""Тесты модуля форматирования app.bot.formatting."""

from datetime import date, time, timedelta
from unittest.mock import MagicMock

from app.bot.formatting import (
    format_date_human,
    format_date_with_weekday,
    format_date_relative,
    format_date_short_with_weekday,
    format_confirmation,
    format_notification,
    format_event_manage_card,
    format_event_edited_notification,
    format_event_deleted_notification,
    format_space_deleted_notification,
    format_conflict_warning,
    get_parse_error_message,
    get_stt_error_message,
)


class TestFormatDateHuman:
    def test_ru(self):
        result = format_date_human(date(2026, 3, 27), "ru")
        assert result == "27 марта 2026"

    def test_en(self):
        result = format_date_human(date(2026, 3, 27), "en")
        assert result == "27 March 2026"


class TestFormatDateWithWeekday:
    def test_ru(self):
        # 27 марта 2026 — пятница
        result = format_date_with_weekday(date(2026, 3, 27), "ru")
        assert "27 марта 2026" in result
        assert "пятница" in result

    def test_en(self):
        result = format_date_with_weekday(date(2026, 3, 27), "en")
        assert "27 March 2026" in result
        assert "Friday" in result


class TestFormatDateRelative:
    def test_today(self):
        today = date.today()
        result = format_date_relative(today, "ru")
        assert result == "сегодня"

    def test_tomorrow(self):
        tomorrow = date.today() + timedelta(days=1)
        result = format_date_relative(tomorrow, "ru")
        assert result == "завтра"

    def test_day_after_tomorrow(self):
        day_after = date.today() + timedelta(days=2)
        result = format_date_relative(day_after, "ru")
        assert result == "послезавтра"

    def test_3_to_6_days(self):
        d = date.today() + timedelta(days=4)
        result = format_date_relative(d, "ru")
        # Должен быть день недели в винительном падеже
        assert result.startswith("в ")

    def test_far_future(self):
        d = date.today() + timedelta(days=30)
        result = format_date_relative(d, "ru")
        # Формат "день месяц"
        assert str(d.day) in result


class TestFormatDateShortWithWeekday:
    def test_ru(self):
        result = format_date_short_with_weekday(date(2026, 3, 28), "ru")
        assert "28 марта" in result
        assert "суббота" in result


class TestFormatConfirmation:
    def test_basic(self):
        result = format_confirmation("Ужин", date(2026, 4, 1), time(19, 0), lang="ru")
        assert "Ужин" in result
        assert "19:00" in result
        assert "Опубликовать?" in result

    def test_without_time(self):
        result = format_confirmation("Поездка", date(2026, 4, 1), None, lang="ru")
        assert "Поездка" in result
        assert "⏰" not in result

    def test_with_transcript(self):
        result = format_confirmation("Ужин", date(2026, 4, 1), time(19, 0),
                                     transcript="ужин завтра", lang="ru")
        assert "ужин завтра" in result

    def test_with_conflict_warning(self):
        result = format_confirmation("Ужин", date(2026, 4, 1), time(19, 0),
                                     conflict_warning="⚠️ Конфликт", lang="ru")
        assert "⚠️ Конфликт" in result

    def test_with_recurrence(self):
        result = format_confirmation("Планёрка", date(2026, 4, 1), time(10, 0),
                                     recurrence_rule="weekly", lang="ru")
        assert "Каждую неделю" in result


class TestFormatNotification:
    def test_basic(self):
        result = format_notification("Семья", "Ужин", date.today(), time(19, 0),
                                     "Иван", lang="ru")
        assert "Семья" in result
        assert "Ужин" in result
        assert "19:00" in result
        assert "Иван" in result

    def test_without_time(self):
        result = format_notification("Семья", "Поездка", date.today(), None,
                                     "Иван", lang="ru")
        assert "⏰" not in result

    def test_with_recurrence(self):
        result = format_notification("Работа", "Планёрка", date.today(), time(10, 0),
                                     "Мария", recurrence_rule="daily", lang="ru")
        assert "Каждый день" in result


class TestFormatEventManageCard:
    def test_basic(self):
        result = format_event_manage_card("Ужин", date(2026, 4, 1), time(19, 0), lang="ru")
        assert "Ужин" in result
        assert "19:00" in result

    def test_without_time(self):
        result = format_event_manage_card("Поездка", date(2026, 4, 1), None, lang="ru")
        assert "⏰" not in result


class TestFormatEventEditedNotification:
    def test_basic(self):
        changes = [("Дата", "1 апреля", "2 апреля")]
        result = format_event_edited_notification("Семья", "Ужин", changes, "Иван", lang="ru")
        assert "Семья" in result
        assert "Ужин" in result
        assert "1 апреля" in result
        assert "2 апреля" in result
        assert "Иван" in result


class TestFormatEventDeletedNotification:
    def test_basic(self):
        result = format_event_deleted_notification("Семья", "Ужин", "Иван", lang="ru")
        assert "Семья" in result
        assert "Ужин" in result
        assert "Иван" in result

    def test_with_date_and_time(self):
        result = format_event_deleted_notification(
            "Семья", "Ужин", "Иван",
            event_date=date(2026, 4, 1), event_time=time(19, 0), lang="ru"
        )
        assert "19:00" in result

    def test_with_date_only(self):
        result = format_event_deleted_notification(
            "Семья", "Ужин", "Иван",
            event_date=date(2026, 4, 1), lang="ru"
        )
        assert "📅" in result


class TestFormatSpaceDeletedNotification:
    def test_basic(self):
        result = format_space_deleted_notification("Семья", "Иван", lang="ru")
        assert "Семья" in result
        assert "Иван" in result


class TestFormatConflictWarning:
    def test_with_events(self):
        ev1 = MagicMock()
        ev1.title = "Встреча"
        ev1.event_time = time(15, 0)
        ev2 = MagicMock()
        ev2.title = "Звонок"
        ev2.event_time = None
        result = format_conflict_warning([ev1, ev2], lang="ru")
        assert "Встреча" in result
        assert "15:00" in result
        assert "Звонок" in result


class TestErrorMessages:
    def test_parse_error(self):
        result = get_parse_error_message("ru", "timeout")
        assert "сервис" in result.lower()

    def test_stt_error(self):
        result = get_stt_error_message("ru", "empty_result")
        assert "речь" in result.lower()
