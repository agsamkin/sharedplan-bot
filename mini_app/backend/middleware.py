"""Middleware для aiohttp веб-сервера Mini App.

Три middleware:
- error_middleware — перехват необработанных исключений, возврат 500 JSON.
- auth_middleware — валидация Telegram initData из заголовка Authorization.
- db_session_middleware — создание/коммит/откат SQLAlchemy-сессии на каждый запрос.
"""

import logging

from aiohttp import web

from app.config import settings
from app.db.engine import async_session
from mini_app.backend.auth import validate_init_data

logger = logging.getLogger(__name__)


@web.middleware
async def error_middleware(request: web.Request, handler) -> web.StreamResponse:
    """Перехват необработанных исключений — возвращает 500 JSON и логирует ошибку."""
    try:
        return await handler(request)
    except web.HTTPException:
        # HTTP-исключения aiohttp (4xx, 3xx) пробрасываем как есть
        raise
    except Exception as e:
        logger.exception("Необработанная ошибка в запросе %s %s: %s", request.method, request.path, e)
        return web.json_response(
            {"error": "Внутренняя ошибка сервера"},
            status=500,
        )


@web.middleware
async def auth_middleware(request: web.Request, handler) -> web.StreamResponse:
    """Валидация Telegram initData для API-запросов.

    Формат заголовка: Authorization: tma <initData>
    Пропускает запросы, не начинающиеся с /api/ (статика, SPA).
    При успешной валидации сохраняет user_id в request["user_id"].
    """
    # Пропускаем не-API пути (статика, SPA fallback)
    if not request.path.startswith("/api/"):
        return await handler(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("tma "):
        return web.json_response(
            {"error": "Отсутствует или невалидный заголовок Authorization"},
            status=401,
        )

    init_data = auth_header[4:]  # убираем префикс "tma "
    try:
        user_id = validate_init_data(init_data, settings.TELEGRAM_BOT_TOKEN)
    except ValueError as e:
        logger.warning("Ошибка авторизации Mini App: %s", e)
        return web.json_response(
            {"error": f"Ошибка авторизации: {e}"},
            status=401,
        )

    request["user_id"] = user_id
    return await handler(request)


@web.middleware
async def db_session_middleware(request: web.Request, handler) -> web.StreamResponse:
    """Создание SQLAlchemy async-сессии на каждый запрос.

    Коммит при успешном ответе, откат при ошибке.
    Сессия доступна через request["session"].
    """
    # Для не-API путей сессия не нужна
    if not request.path.startswith("/api/"):
        return await handler(request)

    async with async_session() as session:
        request["session"] = session
        try:
            response = await handler(request)
            await session.commit()
            return response
        except Exception:
            await session.rollback()
            raise
