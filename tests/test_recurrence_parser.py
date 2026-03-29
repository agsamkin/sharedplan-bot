"""Тесты для поддержки recurrence_rule в парсере событий."""

from datetime import date, time

import pytest
from pydantic import ValidationError

from app.services.llm_parser import ParsedEvent
from app.prompts.event_parser import build_examples, build_system_prompt


class TestParsedEventRecurrence:
    """Тесты валидации recurrence_rule в ParsedEvent."""

    def test_valid_weekly(self):
        event = ParsedEvent.model_validate(
            {"title": "Встреча", "date": "2026-04-01", "time": "15:00", "recurrence_rule": "weekly"}
        )
        assert event.recurrence_rule == "weekly"

    def test_valid_daily(self):
        event = ParsedEvent.model_validate(
            {"title": "Планёрка", "date": "2026-04-01", "time": "10:00", "recurrence_rule": "daily"}
        )
        assert event.recurrence_rule == "daily"

    def test_valid_monthly(self):
        event = ParsedEvent.model_validate(
            {"title": "Собрание", "date": "2026-04-01", "time": None, "recurrence_rule": "monthly"}
        )
        assert event.recurrence_rule == "monthly"

    def test_null_recurrence(self):
        event = ParsedEvent.model_validate(
            {"title": "Ужин", "date": "2026-04-01", "time": "19:00", "recurrence_rule": None}
        )
        assert event.recurrence_rule is None

    def test_missing_recurrence(self):
        event = ParsedEvent.model_validate(
            {"title": "Ужин", "date": "2026-04-01", "time": "19:00"}
        )
        assert event.recurrence_rule is None

    def test_invalid_recurrence(self):
        with pytest.raises(ValidationError):
            ParsedEvent.model_validate(
                {"title": "Test", "date": "2026-04-01", "time": "10:00", "recurrence_rule": "every_3_days"}
            )

    @pytest.mark.parametrize("rule", ["daily", "weekly", "biweekly", "monthly", "yearly"])
    def test_all_valid_rules(self, rule):
        event = ParsedEvent.model_validate(
            {"title": "Test", "date": "2026-04-01", "time": "10:00", "recurrence_rule": rule}
        )
        assert event.recurrence_rule == rule


class TestPromptIncludesRecurrence:
    """Тесты что промпт содержит информацию о повторениях."""

    def test_examples_include_recurrence(self):
        examples = build_examples(date(2026, 3, 29))
        assert "recurrence_rule" in examples
        assert '"weekly"' in examples
        assert '"yearly"' in examples
        assert '"daily"' in examples

    def test_system_prompt_includes_recurrence_rules(self):
        prompt = build_system_prompt(date(2026, 3, 29), time(12, 0))
        assert "recurrence_rule" in prompt
        assert "ежедневно" in prompt.lower() or "каждый день" in prompt.lower()
        assert "каждую неделю" in prompt.lower() or "еженедельно" in prompt.lower()
