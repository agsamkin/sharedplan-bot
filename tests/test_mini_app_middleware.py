"""Тесты middleware Mini App (error, auth, db_session)."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web

# Мокаем зависимости до импорта middleware
_mock_config = MagicMock()
_mock_config.settings = MagicMock()
_mock_config.settings.TELEGRAM_BOT_TOKEN = "test-bot-token"
sys.modules.setdefault("app.config", _mock_config)
sys.modules.setdefault("app.db.engine", MagicMock())
sys.modules.setdefault("app.db.models", MagicMock())

_mock_auth = MagicMock()
sys.modules.setdefault("mini_app.backend.auth", _mock_auth)

from mini_app.backend.middleware import (  # noqa: E402
    error_middleware,
    auth_middleware,
    db_session_middleware,
)


def _make_request(path="/api/test", headers=None):
    request = MagicMock()
    request.path = path
    request.method = "GET"
    request.headers = headers or {}
    store = {}
    request.__setitem__ = lambda self, k, v: store.__setitem__(k, v)
    request.__getitem__ = lambda self, k: store[k]
    return request


# ── error_middleware ──


@pytest.mark.asyncio
async def test_error_middleware_success():
    request = _make_request()
    handler = AsyncMock(return_value=web.Response(text="ok"))

    resp = await error_middleware(request, handler)
    assert resp.status == 200


@pytest.mark.asyncio
async def test_error_middleware_http_exception():
    request = _make_request()
    handler = AsyncMock(side_effect=web.HTTPNotFound())

    with pytest.raises(web.HTTPNotFound):
        await error_middleware(request, handler)


@pytest.mark.asyncio
async def test_error_middleware_generic_exception():
    request = _make_request()
    handler = AsyncMock(side_effect=RuntimeError("boom"))

    resp = await error_middleware(request, handler)
    assert resp.status == 500


# ── auth_middleware ──


@pytest.mark.asyncio
async def test_auth_middleware_non_api_path():
    request = _make_request(path="/static/app.js")
    handler = AsyncMock(return_value=web.Response(text="ok"))

    resp = await auth_middleware(request, handler)
    assert resp.status == 200


@pytest.mark.asyncio
async def test_auth_middleware_missing_header():
    request = _make_request(headers={})
    request.headers = {}
    handler = AsyncMock()

    resp = await auth_middleware(request, handler)
    assert resp.status == 401


@pytest.mark.asyncio
async def test_auth_middleware_invalid_prefix():
    request = _make_request(headers={"Authorization": "Bearer token"})
    handler = AsyncMock()

    resp = await auth_middleware(request, handler)
    assert resp.status == 401


@pytest.mark.asyncio
async def test_auth_middleware_valid():
    request = _make_request(headers={"Authorization": "tma valid-init-data"})
    handler = AsyncMock(return_value=web.Response(text="ok"))

    with patch("mini_app.backend.middleware.validate_init_data", return_value=42):
        resp = await auth_middleware(request, handler)

    assert resp.status == 200
    assert request["user_id"] == 42


@pytest.mark.asyncio
async def test_auth_middleware_validation_error():
    request = _make_request(headers={"Authorization": "tma bad-data"})
    handler = AsyncMock()

    with patch(
        "mini_app.backend.middleware.validate_init_data",
        side_effect=ValueError("invalid hash"),
    ):
        resp = await auth_middleware(request, handler)

    assert resp.status == 401


# ── db_session_middleware ──


@pytest.mark.asyncio
async def test_db_session_middleware_non_api_path():
    request = _make_request(path="/index.html")
    handler = AsyncMock(return_value=web.Response(text="ok"))

    resp = await db_session_middleware(request, handler)
    assert resp.status == 200


@pytest.mark.asyncio
async def test_db_session_middleware_success():
    request = _make_request()
    handler = AsyncMock(return_value=web.Response(text="ok"))

    mock_session = AsyncMock()
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("mini_app.backend.middleware.async_session", return_value=mock_ctx):
        resp = await db_session_middleware(request, handler)

    assert resp.status == 200
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_db_session_middleware_error_rollback():
    request = _make_request()
    handler = AsyncMock(side_effect=RuntimeError("db error"))

    mock_session = AsyncMock()
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("mini_app.backend.middleware.async_session", return_value=mock_ctx):
        with pytest.raises(RuntimeError):
            await db_session_middleware(request, handler)

    mock_session.rollback.assert_awaited_once()
