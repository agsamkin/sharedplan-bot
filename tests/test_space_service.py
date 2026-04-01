"""Тесты space_service — бизнес-логика пространств."""

import sys
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

from app.services.space_service import (  # noqa: E402
    create_space,
    _generate_invite_code,
    get_user_spaces,
    get_space_by_invite_code,
    get_space_by_id,
    join_space,
    get_space_members,
    check_admin,
    find_member_by_username,
    kick_member,
    update_space_name,
    delete_space,
)


class TestCreateSpace:
    @pytest.mark.asyncio
    async def test_creates_space_and_membership(self):
        session = AsyncMock()
        session.scalar = AsyncMock(return_value=None)  # no collision

        space = await create_space(session, 100, "Семья")
        assert space.name == "Семья"
        assert space.created_by == 100
        assert session.add.call_count == 2  # space + membership
        assert session.flush.call_count == 2


class TestGenerateInviteCode:
    @pytest.mark.asyncio
    async def test_generates_unique_code(self):
        session = AsyncMock()
        session.scalar = AsyncMock(return_value=None)

        code = await _generate_invite_code(session)
        assert isinstance(code, str)
        assert len(code) > 0

    @pytest.mark.asyncio
    async def test_retries_on_collision(self):
        session = AsyncMock()
        # Первые 2 попытки — коллизия, третья — успех
        session.scalar = AsyncMock(side_effect=[uuid4(), uuid4(), None])

        code = await _generate_invite_code(session)
        assert isinstance(code, str)

    @pytest.mark.asyncio
    async def test_raises_on_max_attempts(self):
        session = AsyncMock()
        session.scalar = AsyncMock(return_value=uuid4())  # всегда коллизия

        with pytest.raises(RuntimeError, match="invite"):
            await _generate_invite_code(session, max_attempts=3)


class TestGetUserSpaces:
    @pytest.mark.asyncio
    async def test_returns_list(self):
        session = AsyncMock()
        row = MagicMock()
        row.id = uuid4()
        row.name = "Семья"
        row.role = "admin"
        row.member_count = 2
        result_mock = MagicMock()
        result_mock.all.return_value = [row]
        session.execute = AsyncMock(return_value=result_mock)

        result = await get_user_spaces(session, 100)
        assert len(result) == 1
        assert result[0]["name"] == "Семья"
        assert result[0]["role"] == "admin"

    @pytest.mark.asyncio
    async def test_empty_spaces(self):
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.all.return_value = []
        session.execute = AsyncMock(return_value=result_mock)

        result = await get_user_spaces(session, 100)
        assert result == []


class TestGetSpaceByInviteCode:
    @pytest.mark.asyncio
    async def test_found(self):
        session = AsyncMock()
        mock_space = MagicMock()
        session.scalar = AsyncMock(return_value=mock_space)

        result = await get_space_by_invite_code(session, "abc123")
        assert result is mock_space

    @pytest.mark.asyncio
    async def test_not_found(self):
        session = AsyncMock()
        session.scalar = AsyncMock(return_value=None)

        result = await get_space_by_invite_code(session, "nonexistent")
        assert result is None


class TestGetSpaceById:
    @pytest.mark.asyncio
    async def test_found(self):
        session = AsyncMock()
        mock_space = MagicMock()
        session.get = AsyncMock(return_value=mock_space)

        result = await get_space_by_id(session, uuid4())
        assert result is mock_space


class TestJoinSpace:
    @pytest.mark.asyncio
    async def test_new_member(self):
        session = AsyncMock()
        session.get = AsyncMock(return_value=None)  # не участник

        result = await join_space(session, 200, uuid4())
        assert result is not None
        session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_already_member(self):
        session = AsyncMock()
        existing = MagicMock()
        session.get = AsyncMock(return_value=existing)

        result = await join_space(session, 200, uuid4())
        assert result is None


class TestGetSpaceMembers:
    @pytest.mark.asyncio
    async def test_returns_list(self):
        session = AsyncMock()
        row = MagicMock()
        row.id = 100
        row.first_name = "Иван"
        row.username = "ivan"
        row.role = "admin"
        row.joined_at = MagicMock()
        row.joined_at.isoformat.return_value = "2026-03-01T00:00:00"
        result_mock = MagicMock()
        result_mock.all.return_value = [row]
        session.execute = AsyncMock(return_value=result_mock)

        result = await get_space_members(session, uuid4())
        assert len(result) == 1
        assert result[0]["user_id"] == 100
        assert result[0]["role"] == "admin"


class TestCheckAdmin:
    @pytest.mark.asyncio
    async def test_is_admin(self):
        session = AsyncMock()
        membership = MagicMock()
        membership.role = "admin"
        session.get = AsyncMock(return_value=membership)

        assert await check_admin(session, uuid4(), 100) is True

    @pytest.mark.asyncio
    async def test_is_member(self):
        session = AsyncMock()
        membership = MagicMock()
        membership.role = "member"
        session.get = AsyncMock(return_value=membership)

        assert await check_admin(session, uuid4(), 100) is False

    @pytest.mark.asyncio
    async def test_not_member(self):
        session = AsyncMock()
        session.get = AsyncMock(return_value=None)

        assert await check_admin(session, uuid4(), 100) is False


class TestFindMemberByUsername:
    @pytest.mark.asyncio
    async def test_found(self):
        session = AsyncMock()
        row = MagicMock()
        row.id = 100
        row.first_name = "Иван"
        row.username = "ivan"
        row.role = "admin"
        result_mock = MagicMock()
        result_mock.first.return_value = row
        session.execute = AsyncMock(return_value=result_mock)

        result = await find_member_by_username(session, uuid4(), "ivan")
        assert result["user_id"] == 100

    @pytest.mark.asyncio
    async def test_not_found(self):
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.first.return_value = None
        session.execute = AsyncMock(return_value=result_mock)

        result = await find_member_by_username(session, uuid4(), "nobody")
        assert result is None


class TestKickMember:
    @pytest.mark.asyncio
    async def test_kicks(self):
        session = AsyncMock()
        await kick_member(session, uuid4(), 200)
        session.execute.assert_called_once()
        session.flush.assert_called_once()


class TestUpdateSpaceName:
    @pytest.mark.asyncio
    async def test_updates(self):
        session = AsyncMock()
        mock_space = MagicMock()
        session.get = AsyncMock(return_value=mock_space)

        result = await update_space_name(session, uuid4(), "Новое имя")
        assert result is mock_space
        assert mock_space.name == "Новое имя"

    @pytest.mark.asyncio
    async def test_not_found(self):
        session = AsyncMock()
        session.get = AsyncMock(return_value=None)

        result = await update_space_name(session, uuid4(), "Тест")
        assert result is None


class TestDeleteSpace:
    @pytest.mark.asyncio
    async def test_deletes(self):
        session = AsyncMock()
        mock_space = MagicMock()
        session.get = AsyncMock(return_value=mock_space)

        await delete_space(session, uuid4())
        session.delete.assert_called_once_with(mock_space)
        session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_not_found_noop(self):
        session = AsyncMock()
        session.get = AsyncMock(return_value=None)

        await delete_space(session, uuid4())
        session.delete.assert_not_called()
