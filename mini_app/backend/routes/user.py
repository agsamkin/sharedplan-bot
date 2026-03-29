"""API-маршруты для пользовательских настроек.

Эндпоинты:
- GET /api/user/reminders — получить настройки напоминаний пользователя
- PUT /api/user/reminders — обновить настройки напоминаний (частичное обновление)
"""

import logging

from aiohttp import web

from app.db.models import User

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get("/api/user/reminders")
async def get_reminder_settings(request: web.Request) -> web.Response:
    """Получить текущие настройки напоминаний пользователя."""
    user_id: int = request["user_id"]
    session = request["session"]

    user = await session.get(User, user_id)
    if user is None:
        return web.json_response({"error": "Пользователь не найден"}, status=404)

    return web.json_response(user.reminder_settings or {})


@routes.put("/api/user/reminders")
async def update_reminder_settings(request: web.Request) -> web.Response:
    """Обновить настройки напоминаний пользователя.

    Принимает JSON с ключами напоминаний (1d, 2h, 1h, 30m, 15m, 0m).
    Мержит в существующие настройки (не заменяет все целиком).
    """
    user_id: int = request["user_id"]
    session = request["session"]

    user = await session.get(User, user_id)
    if user is None:
        return web.json_response({"error": "Пользователь не найден"}, status=404)

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Невалидный JSON"}, status=400)

    if not isinstance(body, dict):
        return web.json_response({"error": "Ожидается JSON-объект"}, status=400)

    # Мержим: обновляем только переданные ключи
    current_settings = dict(user.reminder_settings or {})
    current_settings.update(body)
    user.reminder_settings = current_settings

    await session.flush()

    return web.json_response(user.reminder_settings)


SUPPORTED_LANGUAGES = ("ru", "en")


@routes.get("/api/user/language")
async def get_language(request: web.Request) -> web.Response:
    """Получить текущий язык интерфейса пользователя."""
    user_id: int = request["user_id"]
    session = request["session"]

    user = await session.get(User, user_id)
    if user is None:
        return web.json_response({"error": "User not found"}, status=404)

    return web.json_response({"language": user.language})


@routes.put("/api/user/language")
async def update_language(request: web.Request) -> web.Response:
    """Обновить язык интерфейса пользователя."""
    user_id: int = request["user_id"]
    session = request["session"]

    user = await session.get(User, user_id)
    if user is None:
        return web.json_response({"error": "User not found"}, status=404)

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    language = body.get("language")
    if language not in SUPPORTED_LANGUAGES:
        return web.json_response(
            {"error": "Invalid language. Supported: ru, en"}, status=400,
        )

    user.language = language
    await session.flush()

    return web.json_response({"language": user.language})
