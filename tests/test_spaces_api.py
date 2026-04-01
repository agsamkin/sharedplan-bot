"""Тесты API пространств (spaces) — list, create, get, update, delete, kick."""

import json
import sys
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Мокаем зависимости
sys.modules.setdefault("app.db.models", MagicMock())
sys.modules.setdefault("app.db.engine", MagicMock())

import app.services  # noqa: E402, F401
_mock_space_service = MagicMock()
sys.modules.setdefault("app.services.space_service", _mock_space_service)

from mini_app.backend.routes.spaces import (  # noqa: E402
    list_spaces,
    create_space,
    get_space,
    update_space,
    delete_space,
    kick_member,
)


def _make_request(user_id=123, json_body=None, json_error=False, match_info=None, bot=None):
    session = AsyncMock()
    request = MagicMock()
    store = {"user_id": user_id, "session": session}
    request.__getitem__ = lambda self, key: store[key]
    request.match_info = match_info or {}
    request.app = {"bot": bot} if bot else {}
    if json_error:
        request.json = AsyncMock(side_effect=Exception("bad json"))
    elif json_body is not None:
        request.json = AsyncMock(return_value=json_body)
    else:
        request.json = AsyncMock(return_value={})
    return request, session


def _make_space(name="Семья", invite_code="ABC123", created_by=123, space_id=None):
    sp = MagicMock()
    sp.id = space_id or uuid.uuid4()
    sp.name = name
    sp.invite_code = invite_code
    sp.created_by = created_by
    return sp


# ── GET /api/spaces ──


class TestListSpaces:
    @pytest.mark.asyncio
    async def test_success(self):
        request, session = _make_request()
        space_id = uuid.uuid4()

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.get_user_spaces = AsyncMock(return_value=[
                {"id": space_id, "name": "Семья", "role": "admin", "member_count": 2},
            ])
            mock_svc.get_space_by_id = AsyncMock(return_value=_make_space(space_id=space_id))

            resp = await list_spaces(request)

        assert resp.status == 200
        body = json.loads(resp.body)
        assert len(body) == 1
        assert body[0]["name"] == "Семья"


# ── POST /api/spaces ──


class TestCreateSpace:
    @pytest.mark.asyncio
    async def test_success(self):
        request, session = _make_request(json_body={"name": "Работа"})

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.create_space = AsyncMock(return_value=_make_space(name="Работа"))
            resp = await create_space(request)

        assert resp.status == 201

    @pytest.mark.asyncio
    async def test_invalid_json(self):
        request, session = _make_request(json_error=True)
        resp = await create_space(request)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_missing_name(self):
        request, session = _make_request(json_body={})
        resp = await create_space(request)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_empty_name(self):
        request, session = _make_request(json_body={"name": "  "})
        resp = await create_space(request)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_name_too_long(self):
        request, session = _make_request(json_body={"name": "x" * 256})
        resp = await create_space(request)
        assert resp.status == 400


# ── GET /api/spaces/{space_id} ──


class TestGetSpace:
    @pytest.mark.asyncio
    async def test_success(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(match_info={"space_id": sid})
        session.get = AsyncMock(return_value=MagicMock())  # membership exists

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.get_space_by_id = AsyncMock(return_value=_make_space())
            mock_svc.get_space_members = AsyncMock(return_value=[
                {"user_id": 123, "first_name": "Иван", "username": "ivan", "role": "admin", "joined_at": None},
            ])
            resp = await get_space(request)

        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_invalid_uuid(self):
        request, session = _make_request(match_info={"space_id": "not-uuid"})
        resp = await get_space(request)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_not_member(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(match_info={"space_id": sid})
        session.get = AsyncMock(return_value=None)

        resp = await get_space(request)
        assert resp.status == 403

    @pytest.mark.asyncio
    async def test_space_not_found(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(match_info={"space_id": sid})
        session.get = AsyncMock(return_value=MagicMock())

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.get_space_by_id = AsyncMock(return_value=None)
            resp = await get_space(request)

        assert resp.status == 404


# ── PUT /api/spaces/{space_id} ──


class TestUpdateSpace:
    @pytest.mark.asyncio
    async def test_success(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(
            match_info={"space_id": sid}, json_body={"name": "Новое"},
        )

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.check_admin = AsyncMock(return_value=True)
            mock_svc.update_space_name = AsyncMock(return_value=_make_space(name="Новое"))
            mock_svc.get_space_members = AsyncMock(return_value=[])
            resp = await update_space(request)

        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_not_admin(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(
            match_info={"space_id": sid}, json_body={"name": "Новое"},
        )

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.check_admin = AsyncMock(return_value=False)
            resp = await update_space(request)

        assert resp.status == 403

    @pytest.mark.asyncio
    async def test_invalid_uuid(self):
        request, session = _make_request(match_info={"space_id": "bad"})
        resp = await update_space(request)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_invalid_json(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(match_info={"space_id": sid}, json_error=True)

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.check_admin = AsyncMock(return_value=True)
            resp = await update_space(request)

        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_empty_name(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(
            match_info={"space_id": sid}, json_body={"name": ""},
        )

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.check_admin = AsyncMock(return_value=True)
            resp = await update_space(request)

        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_space_not_found(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(
            match_info={"space_id": sid}, json_body={"name": "Новое"},
        )

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.check_admin = AsyncMock(return_value=True)
            mock_svc.update_space_name = AsyncMock(return_value=None)
            resp = await update_space(request)

        assert resp.status == 404


# ── DELETE /api/spaces/{space_id} ──


class TestDeleteSpace:
    @pytest.mark.asyncio
    async def test_success_no_bot(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(match_info={"space_id": sid})

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.check_admin = AsyncMock(return_value=True)
            mock_svc.get_space_by_id = AsyncMock(return_value=_make_space())
            mock_svc.get_space_members = AsyncMock(return_value=[])
            mock_svc.delete_space = AsyncMock()
            session.get = AsyncMock(return_value=MagicMock(first_name="Иван"))

            resp = await delete_space(request)

        assert resp.status == 204

    @pytest.mark.asyncio
    async def test_success_with_notification(self):
        sid = str(uuid.uuid4())
        bot = AsyncMock()
        request, session = _make_request(match_info={"space_id": sid}, bot=bot)

        member_user = MagicMock()
        member_user.language = "ru"
        member_user.first_name = "Пётр"
        admin_user = MagicMock()
        admin_user.first_name = "Иван"
        session.get = AsyncMock(side_effect=[admin_user, member_user])

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.check_admin = AsyncMock(return_value=True)
            mock_svc.get_space_by_id = AsyncMock(return_value=_make_space())
            mock_svc.get_space_members = AsyncMock(return_value=[
                {"user_id": 123, "first_name": "Иван", "role": "admin"},
                {"user_id": 456, "first_name": "Пётр", "role": "member"},
            ])
            mock_svc.delete_space = AsyncMock()

            resp = await delete_space(request)

        assert resp.status == 204
        bot.send_message.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_not_admin(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(match_info={"space_id": sid})

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.check_admin = AsyncMock(return_value=False)
            resp = await delete_space(request)

        assert resp.status == 403

    @pytest.mark.asyncio
    async def test_invalid_uuid(self):
        request, session = _make_request(match_info={"space_id": "bad"})
        resp = await delete_space(request)
        assert resp.status == 400


# ── DELETE /api/spaces/{space_id}/members/{member_user_id} ──


class TestKickMember:
    @pytest.mark.asyncio
    async def test_success(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(
            match_info={"space_id": sid, "member_user_id": "456"},
        )

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.check_admin = AsyncMock(return_value=True)
            mock_svc.kick_member = AsyncMock()
            resp = await kick_member(request)

        assert resp.status == 204

    @pytest.mark.asyncio
    async def test_cannot_kick_self(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(
            user_id=123,
            match_info={"space_id": sid, "member_user_id": "123"},
        )
        resp = await kick_member(request)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_not_admin(self):
        sid = str(uuid.uuid4())
        request, session = _make_request(
            match_info={"space_id": sid, "member_user_id": "456"},
        )

        with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
            mock_svc.check_admin = AsyncMock(return_value=False)
            resp = await kick_member(request)

        assert resp.status == 403

    @pytest.mark.asyncio
    async def test_invalid_params(self):
        request, session = _make_request(
            match_info={"space_id": "bad", "member_user_id": "not-int"},
        )
        resp = await kick_member(request)
        assert resp.status == 400
