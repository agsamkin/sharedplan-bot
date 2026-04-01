"""Тесты API списка событий: формат ответа, limit, total_count.

Тесты мокают модуль app.db.models для совместимости с окружениями
без SQLAlchemy 2.0 (DeclarativeBase). Полные интеграционные тесты
запускаются в Docker.
"""

import json
import sys
import uuid
from datetime import date, time, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Мокаем app.db.models до импорта routes, чтобы избежать ImportError
_mock_models = MagicMock()
_mock_models.Event = MagicMock()
_mock_models.Space = MagicMock()
_mock_models.User = MagicMock()
_mock_models.UserSpace = MagicMock()
sys.modules.setdefault("app.db.models", _mock_models)

# Импортируем реальный пакет app.services (__init__.py пустой),
# чтобы setdefault не подменял его MagicMock-ом и не ломал
# импорт app.services.* в других тестах.
import app.services  # noqa: E402, F401

_mock_event_service = MagicMock()
_mock_reminder_service = MagicMock()
sys.modules.setdefault("app.services.event_service", _mock_event_service)
sys.modules.setdefault("app.services.reminder_service", _mock_reminder_service)

# Мокаем app.config
_mock_config = MagicMock()
_mock_config.settings = MagicMock()
_mock_config.settings.TIMEZONE = "Europe/Moscow"
sys.modules.setdefault("app.config", _mock_config)

# Мокаем app.db.engine
sys.modules.setdefault("app.db.engine", MagicMock())

from mini_app.backend.routes.events import list_events  # noqa: E402


def _make_event(
    title: str = "Тест",
    event_date: date | None = None,
    event_time: time | None = None,
    created_by: int = 100,
) -> MagicMock:
    ev = MagicMock()
    ev.id = uuid.uuid4()
    ev.title = title
    ev.event_date = event_date or date(2026, 4, 10)
    ev.event_time = event_time
    ev.created_by = created_by
    ev.created_at = datetime(2026, 3, 29, 12, 0, 0)
    ev.space_id = uuid.uuid4()
    ev.recurrence_rule = None
    return ev


def _make_user(user_id: int = 100, first_name: str = "Иван") -> MagicMock:
    user = MagicMock()
    user.id = user_id
    user.first_name = first_name
    return user


def _make_membership() -> MagicMock:
    m = MagicMock()
    m.user_id = 100
    m.role = "member"
    return m


@pytest.fixture
def space_id():
    return uuid.uuid4()


def _make_request(space_id, user_id: int = 200, query: dict | None = None):
    from aiohttp import web

    request = MagicMock(spec=web.Request)
    session = AsyncMock()
    store = {"user_id": user_id, "session": session}
    request.__getitem__ = MagicMock(side_effect=lambda k: store[k])
    request.match_info = {"space_id": str(space_id)}
    request.query = query or {}
    return request, session


@pytest.mark.asyncio
async def test_list_events_returns_object_with_events_and_total_count(space_id):
    """GET /api/spaces/:id/events возвращает объект с events и total_count."""
    events = [_make_event(title="Событие 1"), _make_event(title="Событие 2")]
    request, session = _make_request(space_id, user_id=200)

    session.get = AsyncMock(side_effect=lambda model, key: (
        _make_membership() if isinstance(key, tuple) else _make_user()
    ))

    with patch("mini_app.backend.routes.events.event_service") as mock_svc:
        mock_svc.get_upcoming_events = AsyncMock(return_value=events)
        mock_svc.count_upcoming_events = AsyncMock(return_value=2)

        response = await list_events(request)

    body = json.loads(response.text)
    assert "events" in body
    assert "total_count" in body
    assert body["total_count"] == 2
    assert len(body["events"]) == 2
    assert body["events"][0]["title"] == "Событие 1"


@pytest.mark.asyncio
async def test_list_events_limit_param(space_id):
    """Параметр limit передаётся в get_upcoming_events, total_count не зависит от limit."""
    request, session = _make_request(space_id, user_id=200, query={"limit": "2"})

    session.get = AsyncMock(side_effect=lambda model, key: (
        _make_membership() if isinstance(key, tuple) else _make_user()
    ))

    with patch("mini_app.backend.routes.events.event_service") as mock_svc:
        mock_svc.get_upcoming_events = AsyncMock(return_value=[_make_event()])
        mock_svc.count_upcoming_events = AsyncMock(return_value=10)

        response = await list_events(request)

    body = json.loads(response.text)
    # limit=2 передан в сервис
    mock_svc.get_upcoming_events.assert_called_once()
    _, kwargs = mock_svc.get_upcoming_events.call_args
    assert kwargs["limit"] == 2
    # total_count отражает полное количество
    assert body["total_count"] == 10


@pytest.mark.asyncio
async def test_list_events_limit_capped_at_100(space_id):
    """limit > 100 ограничивается до 100."""
    request, session = _make_request(space_id, user_id=200, query={"limit": "500"})

    session.get = AsyncMock(side_effect=lambda model, key: (
        _make_membership() if isinstance(key, tuple) else _make_user()
    ))

    with patch("mini_app.backend.routes.events.event_service") as mock_svc:
        mock_svc.get_upcoming_events = AsyncMock(return_value=[])
        mock_svc.count_upcoming_events = AsyncMock(return_value=0)

        await list_events(request)

    _, kwargs = mock_svc.get_upcoming_events.call_args
    assert kwargs["limit"] == 100
