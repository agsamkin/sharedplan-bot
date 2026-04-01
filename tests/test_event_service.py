"""Тесты event_service — бизнес-логика событий."""

import sys
from datetime import date, datetime, time, timedelta
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

from app.services.event_service import (  # noqa: E402
    create_event,
    _upcoming_events_filter,
    get_upcoming_events,
    count_upcoming_events,
    get_event_for_owner,
    delete_event,
    find_conflicting_events,
    update_event,
)
from app.db.models import Event  # noqa: E402


class TestCreateEvent:
    @pytest.mark.asyncio
    async def test_creates_and_returns_event(self):
        session = AsyncMock()
        space_id = uuid4()
        result = await create_event(
            session, space_id, "Ужин", date(2026, 4, 10), time(19, 0),
            created_by=100, raw_input="Ужин завтра",
        )
        session.add.assert_called_once()
        session.flush.assert_called_once()
        assert result.title == "Ужин"
        assert result.event_date == date(2026, 4, 10)
        assert result.event_time == time(19, 0)

    @pytest.mark.asyncio
    async def test_creates_without_time(self):
        session = AsyncMock()
        result = await create_event(
            session, uuid4(), "Поездка", date(2026, 4, 10), None, created_by=100,
        )
        assert result.event_time is None

    @pytest.mark.asyncio
    async def test_creates_with_recurrence(self):
        session = AsyncMock()
        result = await create_event(
            session, uuid4(), "Планёрка", date(2026, 4, 10), time(10, 0),
            created_by=100, recurrence_rule="weekly",
        )
        assert result.recurrence_rule == "weekly"


class TestUpcomingEventsFilter:
    def test_returns_list_of_conditions(self):
        space_id = uuid4()
        conditions = _upcoming_events_filter(space_id)
        assert isinstance(conditions, list)
        assert len(conditions) > 0


class TestGetUpcomingEvents:
    @pytest.mark.asyncio
    async def test_returns_list(self):
        session = AsyncMock()
        mock_event = MagicMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [mock_event]
        session.execute = AsyncMock(return_value=result_mock)

        with patch("app.services.event_service._advance_stale_recurring_parents", new_callable=AsyncMock):
            result = await get_upcoming_events(session, uuid4(), 10)

        assert isinstance(result, list)
        assert len(result) == 1


class TestCountUpcomingEvents:
    @pytest.mark.asyncio
    async def test_returns_count(self):
        session = AsyncMock()
        session.scalar = AsyncMock(return_value=5)

        with patch("app.services.event_service._advance_stale_recurring_parents", new_callable=AsyncMock):
            result = await count_upcoming_events(session, uuid4())

        assert result == 5

    @pytest.mark.asyncio
    async def test_returns_zero_on_none(self):
        session = AsyncMock()
        session.scalar = AsyncMock(return_value=None)

        with patch("app.services.event_service._advance_stale_recurring_parents", new_callable=AsyncMock):
            result = await count_upcoming_events(session, uuid4())

        assert result == 0


class TestGetEventForOwner:
    @pytest.mark.asyncio
    async def test_found(self):
        session = AsyncMock()
        mock_event = MagicMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_event
        session.execute = AsyncMock(return_value=result_mock)

        result = await get_event_for_owner(session, uuid4(), 100)
        assert result is mock_event

    @pytest.mark.asyncio
    async def test_not_found(self):
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result_mock)

        result = await get_event_for_owner(session, uuid4(), 100)
        assert result is None


class TestDeleteEvent:
    @pytest.mark.asyncio
    async def test_deletes(self):
        session = AsyncMock()
        await delete_event(session, uuid4())
        session.execute.assert_called_once()
        session.flush.assert_called_once()


class TestFindConflictingEvents:
    @pytest.mark.asyncio
    async def test_no_time_returns_empty(self):
        session = AsyncMock()
        result = await find_conflicting_events(session, uuid4(), date(2026, 4, 10), None)
        assert result == []

    @pytest.mark.asyncio
    async def test_with_time_queries(self):
        session = AsyncMock()
        mock_event = MagicMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [mock_event]
        session.execute = AsyncMock(return_value=result_mock)

        result = await find_conflicting_events(
            session, uuid4(), date(2026, 4, 10), time(14, 0),
        )
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_with_exclude_event_id(self):
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result_mock)

        result = await find_conflicting_events(
            session, uuid4(), date(2026, 4, 10), time(14, 0),
            exclude_event_id=uuid4(),
        )
        assert result == []


class TestUpdateEvent:
    @pytest.mark.asyncio
    async def test_updates_fields(self):
        session = AsyncMock()
        mock_event = MagicMock()
        session.get = AsyncMock(return_value=mock_event)

        result = await update_event(session, uuid4(), title="Новый ужин")
        assert result is mock_event
        assert mock_event.title == "Новый ужин"
        session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_not_found_returns_none(self):
        session = AsyncMock()
        session.get = AsyncMock(return_value=None)

        result = await update_event(session, uuid4(), title="Нет")
        assert result is None
