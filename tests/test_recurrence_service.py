"""Тесты для сервиса повторяющихся событий."""

from datetime import date

import pytest

from app.services.recurrence_service import next_occurrence_date, VALID_RECURRENCE_RULES


class TestNextOccurrenceDate:
    """Тесты вычисления следующей даты."""

    def test_daily(self):
        assert next_occurrence_date(date(2026, 3, 29), "daily") == date(2026, 3, 30)

    def test_weekly(self):
        assert next_occurrence_date(date(2026, 3, 29), "weekly") == date(2026, 4, 5)

    def test_biweekly(self):
        assert next_occurrence_date(date(2026, 3, 29), "biweekly") == date(2026, 4, 12)

    def test_monthly(self):
        assert next_occurrence_date(date(2026, 3, 29), "monthly") == date(2026, 4, 29)

    def test_monthly_end_of_month(self):
        # 31 января + 1 месяц = 28 февраля (не-високосный)
        assert next_occurrence_date(date(2027, 1, 31), "monthly") == date(2027, 2, 28)

    def test_monthly_end_of_month_leap(self):
        # 31 января + 1 месяц = 29 февраля (високосный)
        assert next_occurrence_date(date(2028, 1, 31), "monthly") == date(2028, 2, 29)

    def test_monthly_30_to_feb(self):
        # 30 января + 1 месяц = 28 февраля
        assert next_occurrence_date(date(2027, 1, 30), "monthly") == date(2027, 2, 28)

    def test_yearly(self):
        assert next_occurrence_date(date(2026, 4, 5), "yearly") == date(2027, 4, 5)

    def test_yearly_leap_day(self):
        # 29 февраля + 1 год = 28 февраля
        assert next_occurrence_date(date(2028, 2, 29), "yearly") == date(2029, 2, 28)

    def test_invalid_rule(self):
        with pytest.raises(ValueError):
            next_occurrence_date(date(2026, 3, 29), "every_3_days")


class TestValidRules:
    """Тесты набора допустимых правил."""

    def test_all_rules_present(self):
        assert VALID_RECURRENCE_RULES == {"daily", "weekly", "biweekly", "monthly", "yearly"}

    @pytest.mark.parametrize("rule", ["daily", "weekly", "biweekly", "monthly", "yearly"])
    def test_each_rule_computes(self, rule):
        result = next_occurrence_date(date(2026, 6, 15), rule)
        assert result > date(2026, 6, 15)
