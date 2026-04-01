"""Тесты модуля интернационализации app.i18n."""

from app.i18n import (
    normalize_language,
    t,
    get_reminder_labels,
    get_relative_labels,
    get_recurrence_label,
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
)


class TestNormalizeLanguage:
    def test_ru(self):
        assert normalize_language("ru") == "ru"

    def test_ru_prefix(self):
        assert normalize_language("ru_RU") == "ru"

    def test_en(self):
        assert normalize_language("en") == "en"

    def test_none(self):
        assert normalize_language(None) == "en"

    def test_unknown(self):
        assert normalize_language("fr") == "en"


class TestT:
    def test_ru_key(self):
        result = t("ru", "help.text")
        assert "Создание событий" in result

    def test_en_key(self):
        result = t("en", "help.text")
        assert "Creating events" in result

    def test_missing_key_returns_key(self):
        assert t("ru", "nonexistent.key") == "nonexistent.key"

    def test_unknown_lang_falls_back_to_en(self):
        result = t("fr", "help.text")
        assert "Creating events" in result

    def test_kwargs_interpolation(self):
        result = t("ru", "start.welcome.spaces", names="Семья, Работа")
        assert "Семья, Работа" in result

    def test_kwargs_missing_key_returns_template(self):
        result = t("ru", "start.welcome.spaces", wrong_key="test")
        assert "{names}" in result


class TestGetReminderLabels:
    def test_ru_labels(self):
        labels = get_reminder_labels("ru")
        assert len(labels) == 6
        assert "1d" in labels
        assert "0m" in labels
        assert labels["1d"] == "За 1 день"

    def test_en_labels(self):
        labels = get_reminder_labels("en")
        assert labels["1d"] == "1 day before"


class TestGetRelativeLabels:
    def test_ru_labels(self):
        labels = get_relative_labels("ru")
        assert len(labels) == 6
        assert labels["0m"] == "Сейчас"

    def test_en_labels(self):
        labels = get_relative_labels("en")
        assert labels["0m"] == "Now"


class TestGetRecurrenceLabel:
    def test_none_rule(self):
        assert get_recurrence_label("ru", None) is None

    def test_daily_ru(self):
        assert get_recurrence_label("ru", "daily") == "Каждый день"

    def test_weekly_en(self):
        assert get_recurrence_label("en", "weekly") == "Every week"

    def test_unknown_rule_returns_key(self):
        result = get_recurrence_label("ru", "unknown")
        assert result == "recurrence.unknown"


class TestConstants:
    def test_supported_languages(self):
        assert "ru" in SUPPORTED_LANGUAGES
        assert "en" in SUPPORTED_LANGUAGES

    def test_default_language(self):
        assert DEFAULT_LANGUAGE == "en"
