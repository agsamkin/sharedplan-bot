"""Фабрика aiohttp веб-приложения для Telegram Mini App.

Создаёт и настраивает aiohttp Application:
- Middleware (error, auth, db_session)
- API-маршруты (spaces, events, user)
- Раздача статики SPA (mini_app/frontend/dist/)
- Fallback на index.html для SPA-роутинга
"""

import logging
from pathlib import Path

from aiohttp import web

from mini_app.backend.middleware import auth_middleware, db_session_middleware, error_middleware
from mini_app.backend.routes.events import routes as events_routes
from mini_app.backend.routes.spaces import routes as spaces_routes
from mini_app.backend.routes.user import routes as user_routes

logger = logging.getLogger(__name__)

# Путь к директории со статикой SPA
STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"


async def _spa_fallback_handler(request: web.Request) -> web.StreamResponse:
    """Обработчик SPA fallback: отдаёт index.html для не-API и не-статических путей.

    Это позволяет фронтенду использовать HTML5 History API для роутинга.
    """
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return web.FileResponse(index_path)
    return web.json_response({"error": "Frontend не собран"}, status=404)


def create_web_app(bot) -> web.Application:
    """Создать и сконфигурировать aiohttp Application.

    Args:
        bot: экземпляр aiogram.Bot для отправки уведомлений из API.

    Returns:
        Настроенное aiohttp веб-приложение.
    """
    app = web.Application(
        middlewares=[
            error_middleware,
            auth_middleware,
            db_session_middleware,
        ],
    )

    # Сохраняем бота для использования в маршрутах (уведомления)
    app["bot"] = bot

    # Регистрируем API-маршруты
    app.router.add_routes(spaces_routes)
    app.router.add_routes(events_routes)
    app.router.add_routes(user_routes)

    # Раздача статики SPA (если директория существует)
    if STATIC_DIR.exists():
        # Статические файлы (JS, CSS, изображения и т.д.)
        app.router.add_static("/assets", STATIC_DIR / "assets", show_index=False)
        logger.info("Mini App: статика из %s", STATIC_DIR)
    else:
        logger.warning("Mini App: директория статики не найдена: %s", STATIC_DIR)

    # SPA fallback — catch-all для всех остальных путей
    app.router.add_get("/{path:.*}", _spa_fallback_handler)

    logger.info("Mini App: веб-приложение создано")
    return app
