"""Тесты для сервиса повторяющихся событий."""

import uuid
from datetime import date, datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.recurrence_service import (
    next_occurrence_date,
    VALID_RECURRENCE_RULES,
    advance_parent_date,
    generate_occurrences,
    regenerate_occurrences,
    update_future_occurrences,
)


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


# ── Helpers ──

_TZ = __import__("zoneinfo").ZoneInfo("Europe/Moscow")
_FIXED_NOW = datetime(2026, 4, 1, 12, 0, tzinfo=_TZ)


def _make_parent_event(
    event_date=date(2026, 3, 15),
    event_time=time(10, 0),
    rule="weekly",
):
    e = MagicMock()
    e.id = uuid.uuid4()
    e.space_id = uuid.uuid4()
    e.event_date = event_date
    e.event_time = event_time
    e.recurrence_rule = rule
    e.parent_event_id = None
    e.title = "Тест"
    e.created_by = 123
    e.raw_input = None
    return e


# ── advance_parent_date ──


class TestAdvanceParentDate:
    @pytest.mark.asyncio
    @patch("app.services.recurrence_service.datetime")
    async def test_advances_past_date(self, mock_dt):
        mock_dt.now.return_value = _FIXED_NOW
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

        session = AsyncMock()
        event = _make_parent_event(event_date=date(2026, 3, 15), rule="weekly")

        result = await advance_parent_date(session, event)
        assert result is True
        assert event.event_date > date(2026, 4, 1)

    @pytest.mark.asyncio
    @patch("app.services.recurrence_service.datetime")
    async def test_noop_if_future_date(self, mock_dt):
        mock_dt.now.return_value = _FIXED_NOW

        session = AsyncMock()
        event = _make_parent_event(event_date=date(2026, 5, 1))

        result = await advance_parent_date(session, event)
        assert result is False

    @pytest.mark.asyncio
    async def test_noop_if_child_event(self):
        session = AsyncMock()
        event = _make_parent_event()
        event.parent_event_id = uuid.uuid4()

        result = await advance_parent_date(session, event)
        assert result is False

    @pytest.mark.asyncio
    async def test_noop_if_no_rule(self):
        session = AsyncMock()
        event = _make_parent_event()
        event.recurrence_rule = None

        result = await advance_parent_date(session, event)
        assert result is False

    @pytest.mark.asyncio
    @patch("app.services.recurrence_service.datetime")
    async def test_today_with_future_time_noop(self, mock_dt):
        mock_dt.now.return_value = _FIXED_NOW

        session = AsyncMock()
        event = _make_parent_event(event_date=date(2026, 4, 1), event_time=time(18, 0))

        result = await advance_parent_date(session, event)
        assert result is False

    @pytest.mark.asyncio
    @patch("app.services.recurrence_service.datetime")
    async def test_today_with_past_time_advances(self, mock_dt):
        mock_dt.now.return_value = _FIXED_NOW
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

        session = AsyncMock()
        event = _make_parent_event(
            event_date=date(2026, 4, 1), event_time=time(10, 0), rule="daily",
        )

        result = await advance_parent_date(session, event)
        assert result is True
        assert event.event_date == date(2026, 4, 2)


# ── generate_occurrences ──


class TestGenerateOccurrences:
    @pytest.mark.asyncio
    @patch("app.services.recurrence_service.reminder_service")
    @patch("app.services.recurrence_service.datetime")
    async def test_generates_occurrences(self, mock_dt, mock_reminder_svc):
        mock_dt.now.return_value = _FIXED_NOW
        mock_reminder_svc.create_reminders_for_event = AsyncMock(return_value=1)

        session = AsyncMock()
        # scalar_one_or_none returns None → creates new occurrence
        session.execute = AsyncMock(
            return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        )

        event = _make_parent_event(
            event_date=date(2026, 4, 1), rule="weekly",
        )

        count = await generate_occurrences(session, event, horizon_days=30)
        assert count > 0
        assert session.add.call_count == count

    @pytest.mark.asyncio
    async def test_noop_for_child_event(self):
        session = AsyncMock()
        event = _make_parent_event()
        event.parent_event_id = uuid.uuid4()

        count = await generate_occurrences(session, event)
        assert count == 0

    @pytest.mark.asyncio
    async def test_noop_for_no_rule(self):
        session = AsyncMock()
        event = _make_parent_event()
        event.recurrence_rule = None

        count = await generate_occurrences(session, event)
        assert count == 0

    @pytest.mark.asyncio
    @patch("app.services.recurrence_service.reminder_service")
    @patch("app.services.recurrence_service.datetime")
    async def test_skips_existing_occurrences(self, mock_dt, mock_reminder_svc):
        mock_dt.now.return_value = _FIXED_NOW
        mock_reminder_svc.create_reminders_for_event = AsyncMock(return_value=0)

        session = AsyncMock()
        # Batch-запрос возвращает все целевые даты как существующие → skip all
        event = _make_parent_event(event_date=date(2026, 4, 1), rule="weekly")

        # Вычислить ожидаемые даты (как делает generate_occurrences)
        from app.services.recurrence_service import next_occurrence_date
        expected_dates = []
        td = next_occurrence_date(date(2026, 4, 1), "weekly")
        horizon = _FIXED_NOW.date() + timedelta(days=30)
        while td <= horizon:
            expected_dates.append(td)
            td = next_occurrence_date(td, "weekly")

        # scalars().all() возвращает все существующие даты
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = expected_dates
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        session.execute = AsyncMock(return_value=mock_result)

        count = await generate_occurrences(session, event, horizon_days=30)
        assert count == 0


# ── regenerate_occurrences ──


class TestRegenerateOccurrences:
    @pytest.mark.asyncio
    @patch("app.services.recurrence_service.generate_occurrences", new_callable=AsyncMock)
    async def test_deletes_and_regenerates(self, mock_gen):
        mock_gen.return_value = 5
        session = AsyncMock()
        event = _make_parent_event()

        count = await regenerate_occurrences(session, event, horizon_days=30)
        assert count == 5
        session.execute.assert_awaited()
        mock_gen.assert_awaited_once()


# ── update_future_occurrences ──


class TestUpdateFutureOccurrences:
    @pytest.mark.asyncio
    @patch("app.services.recurrence_service.reminder_service")
    async def test_updates_and_recreates_reminders(self, mock_reminder_svc):
        mock_reminder_svc.recreate_reminders_for_event = AsyncMock(return_value=2)

        session = AsyncMock()
        # First execute returns rowcount=3
        mock_update_result = MagicMock()
        mock_update_result.rowcount = 3
        # Second execute returns list of occurrences
        occ1, occ2, occ3 = MagicMock(), MagicMock(), MagicMock()
        mock_select_result = MagicMock()
        mock_select_result.scalars.return_value.all.return_value = [occ1, occ2, occ3]

        session.execute = AsyncMock(side_effect=[mock_update_result, mock_select_result])

        event = _make_parent_event()
        count = await update_future_occurrences(session, event)

        assert count == 3
        assert mock_reminder_svc.recreate_reminders_for_event.await_count == 3
