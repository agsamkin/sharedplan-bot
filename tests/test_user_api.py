"""Тесты API пользовательских настроек (reminders, language)."""

import json
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

# Мокаем зависимости до импорта routes
sys.modules.setdefault("app.db.models", MagicMock())
sys.modules.setdefault("app.db.engine", MagicMock())

from mini_app.backend.routes.user import (  # noqa: E402
    get_reminder_settings,
    update_reminder_settings,
    get_language,
    update_language,
    SUPPORTED_LANGUAGES,
)


def _make_request(user_id=123, json_body=None, json_error=False):
    """Создать мок aiohttp.web.Request."""
    session = AsyncMock()
    request = MagicMock()
    request.__getitem__ = lambda self, key: {
        "user_id": user_id,
        "session": session,
    }[key]
    if json_error:
        request.json = AsyncMock(side_effect=Exception("bad json"))
    elif json_body is not None:
        request.json = AsyncMock(return_value=json_body)
    else:
        request.json = AsyncMock(return_value={})
    return request, session


def _make_user(reminder_settings=None, language="ru"):
    user = MagicMock()
    user.reminder_settings = reminder_settings
    user.language = language
    return user


# ── GET /api/user/reminders ──


@pytest.mark.asyncio
async def test_get_reminders_success():
    request, session = _make_request()
    user = _make_user(reminder_settings={"1d": True, "2h": False})
    session.get = AsyncMock(return_value=user)

    resp = await get_reminder_settings(request)
    assert resp.status == 200
    body = json.loads(resp.body)
    assert body == {"1d": True, "2h": False}


@pytest.mark.asyncio
async def test_get_reminders_empty():
    request, session = _make_request()
    user = _make_user(reminder_settings=None)
    session.get = AsyncMock(return_value=user)

    resp = await get_reminder_settings(request)
    assert resp.status == 200
    assert json.loads(resp.body) == {}


@pytest.mark.asyncio
async def test_get_reminders_user_not_found():
    request, session = _make_request()
    session.get = AsyncMock(return_value=None)

    resp = await get_reminder_settings(request)
    assert resp.status == 404


# ── PUT /api/user/reminders ──


@pytest.mark.asyncio
async def test_update_reminders_success():
    request, session = _make_request(json_body={"30m": True})
    user = _make_user(reminder_settings={"1d": True})
    session.get = AsyncMock(return_value=user)

    resp = await update_reminder_settings(request)
    assert resp.status == 200
    assert user.reminder_settings == {"1d": True, "30m": True}


@pytest.mark.asyncio
async def test_update_reminders_user_not_found():
    request, session = _make_request(json_body={"1d": True})
    session.get = AsyncMock(return_value=None)

    resp = await update_reminder_settings(request)
    assert resp.status == 404


@pytest.mark.asyncio
async def test_update_reminders_invalid_json():
    request, session = _make_request(json_error=True)
    user = _make_user()
    session.get = AsyncMock(return_value=user)

    resp = await update_reminder_settings(request)
    assert resp.status == 400


@pytest.mark.asyncio
async def test_update_reminders_not_dict():
    request, session = _make_request(json_body=[1, 2, 3])
    user = _make_user()
    session.get = AsyncMock(return_value=user)

    resp = await update_reminder_settings(request)
    assert resp.status == 400


# ── GET /api/user/language ──


@pytest.mark.asyncio
async def test_get_language_success():
    request, session = _make_request()
    user = _make_user(language="en")
    session.get = AsyncMock(return_value=user)

    resp = await get_language(request)
    assert resp.status == 200
    assert json.loads(resp.body) == {"language": "en"}


@pytest.mark.asyncio
async def test_get_language_user_not_found():
    request, session = _make_request()
    session.get = AsyncMock(return_value=None)

    resp = await get_language(request)
    assert resp.status == 404


# ── PUT /api/user/language ──


@pytest.mark.asyncio
async def test_update_language_success():
    request, session = _make_request(json_body={"language": "en"})
    user = _make_user(language="ru")
    session.get = AsyncMock(return_value=user)

    resp = await update_language(request)
    assert resp.status == 200
    assert user.language == "en"


@pytest.mark.asyncio
async def test_update_language_user_not_found():
    request, session = _make_request(json_body={"language": "en"})
    session.get = AsyncMock(return_value=None)

    resp = await update_language(request)
    assert resp.status == 404


@pytest.mark.asyncio
async def test_update_language_invalid_json():
    request, session = _make_request(json_error=True)
    user = _make_user()
    session.get = AsyncMock(return_value=user)

    resp = await update_language(request)
    assert resp.status == 400


@pytest.mark.asyncio
async def test_update_language_unsupported():
    request, session = _make_request(json_body={"language": "de"})
    user = _make_user()
    session.get = AsyncMock(return_value=user)

    resp = await update_language(request)
    assert resp.status == 400


@pytest.mark.asyncio
async def test_update_language_missing_key():
    request, session = _make_request(json_body={})
    user = _make_user()
    session.get = AsyncMock(return_value=user)

    resp = await update_language(request)
    assert resp.status == 400


def test_supported_languages():
    assert "ru" in SUPPORTED_LANGUAGES
    assert "en" in SUPPORTED_LANGUAGES
