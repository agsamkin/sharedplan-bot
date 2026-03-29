"""Тесты уведомления участников при удалении пространства.

Проверяем, что DELETE /api/spaces/{space_id} отправляет уведомления
всем участникам (кроме админа-инициатора) и корректно обрабатывает ошибки.
"""

import sys
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Мокаем модули до импорта routes
_mock_models = MagicMock()
_mock_models.User = MagicMock()
_mock_models.UserSpace = MagicMock()
_mock_models.Space = MagicMock()
sys.modules.setdefault("app.db.models", _mock_models)

_mock_space_service = MagicMock()
_mock_services = MagicMock()
_mock_services.space_service = _mock_space_service
sys.modules.setdefault("app.services", _mock_services)
sys.modules.setdefault("app.services.space_service", _mock_space_service)

_mock_config = MagicMock()
_mock_config.settings = MagicMock()
_mock_config.settings.TIMEZONE = "Europe/Moscow"
sys.modules.setdefault("app.config", _mock_config)
sys.modules.setdefault("app.db.engine", MagicMock())

from mini_app.backend.routes.spaces import delete_space  # noqa: E402


def _make_space(name: str = "Семья") -> MagicMock:
    space = MagicMock()
    space.id = uuid.uuid4()
    space.name = name
    return space


def _make_admin_user(user_id: int = 100, first_name: str = "Иван") -> MagicMock:
    user = MagicMock()
    user.id = user_id
    user.first_name = first_name
    return user


def _make_request(space_id: uuid.UUID, user_id: int = 100, bot=None):
    from aiohttp import web

    request = MagicMock(spec=web.Request)
    session = AsyncMock()
    store = {"user_id": user_id, "session": session}
    request.__getitem__ = MagicMock(side_effect=lambda k: store[k])
    request.match_info = {"space_id": str(space_id)}

    app_store = {"bot": bot}
    request.app = MagicMock()
    request.app.get = MagicMock(side_effect=lambda k, default=None: app_store.get(k, default))

    return request, session


@pytest.mark.asyncio
async def test_delete_space_notifies_all_members_except_admin():
    """При удалении пространства все участники (кроме админа) получают уведомление."""
    space = _make_space("Семья")
    admin = _make_admin_user(100, "Иван")
    members = [
        {"user_id": 100, "first_name": "Иван", "username": "ivan", "role": "admin"},
        {"user_id": 200, "first_name": "Мария", "username": "maria", "role": "member"},
        {"user_id": 300, "first_name": "Пётр", "username": "petr", "role": "member"},
    ]
    bot = AsyncMock()
    request, session = _make_request(space.id, user_id=100, bot=bot)
    session.get = AsyncMock(return_value=admin)

    with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
        mock_svc.check_admin = AsyncMock(return_value=True)
        mock_svc.get_space_by_id = AsyncMock(return_value=space)
        mock_svc.get_space_members = AsyncMock(return_value=members)
        mock_svc.delete_space = AsyncMock()

        response = await delete_space(request)

    assert response.status == 204
    assert bot.send_message.call_count == 2
    notified_ids = [call.args[0] for call in bot.send_message.call_args_list]
    assert 200 in notified_ids
    assert 300 in notified_ids
    assert 100 not in notified_ids
    # Проверяем содержание уведомления
    msg = bot.send_message.call_args_list[0].args[1]
    assert "Семья" in msg
    assert "Иван" in msg


@pytest.mark.asyncio
async def test_delete_space_single_member_no_notifications():
    """Если админ — единственный участник, уведомления не отправляются."""
    space = _make_space("Личное")
    admin = _make_admin_user(100, "Иван")
    members = [
        {"user_id": 100, "first_name": "Иван", "username": "ivan", "role": "admin"},
    ]
    bot = AsyncMock()
    request, session = _make_request(space.id, user_id=100, bot=bot)
    session.get = AsyncMock(return_value=admin)

    with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
        mock_svc.check_admin = AsyncMock(return_value=True)
        mock_svc.get_space_by_id = AsyncMock(return_value=space)
        mock_svc.get_space_members = AsyncMock(return_value=members)
        mock_svc.delete_space = AsyncMock()

        response = await delete_space(request)

    assert response.status == 204
    bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_delete_space_notification_error_does_not_break_response():
    """Ошибка отправки одному участнику не блокирует уведомление остальным и API-ответ."""
    space = _make_space("Работа")
    admin = _make_admin_user(100, "Иван")
    members = [
        {"user_id": 100, "first_name": "Иван", "username": "ivan", "role": "admin"},
        {"user_id": 200, "first_name": "Мария", "username": "maria", "role": "member"},
        {"user_id": 300, "first_name": "Пётр", "username": "petr", "role": "member"},
    ]
    bot = AsyncMock()
    # Первый вызов (user 200) — ошибка, второй (user 300) — успех
    bot.send_message = AsyncMock(side_effect=[Exception("Telegram API error"), None])

    request, session = _make_request(space.id, user_id=100, bot=bot)
    session.get = AsyncMock(return_value=admin)

    with patch("mini_app.backend.routes.spaces.space_service") as mock_svc:
        mock_svc.check_admin = AsyncMock(return_value=True)
        mock_svc.get_space_by_id = AsyncMock(return_value=space)
        mock_svc.get_space_members = AsyncMock(return_value=members)
        mock_svc.delete_space = AsyncMock()

        response = await delete_space(request)

    assert response.status == 204
    # Оба вызова были сделаны, несмотря на ошибку первого
    assert bot.send_message.call_count == 2
