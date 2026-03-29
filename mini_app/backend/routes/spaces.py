"""API-маршруты для работы с пространствами (spaces).

Эндпоинты:
- GET /api/spaces — список пространств пользователя
- POST /api/spaces — создание нового пространства
- GET /api/spaces/{space_id} — информация о пространстве + участники
- PUT /api/spaces/{space_id} — обновление названия пространства (только admin)
- DELETE /api/spaces/{space_id} — удаление пространства (только admin)
- DELETE /api/spaces/{space_id}/members/{user_id} — исключение участника (только admin)
"""

import logging
from uuid import UUID

from aiohttp import web

from app.bot.formatting import format_space_deleted_notification
from app.db.models import User
from app.services import space_service

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get("/api/spaces")
async def list_spaces(request: web.Request) -> web.Response:
    """Список пространств текущего пользователя."""
    user_id: int = request["user_id"]
    session = request["session"]

    spaces = await space_service.get_user_spaces(session, user_id)

    # Для каждого пространства добавляем invite_code
    result = []
    for sp in spaces:
        space_obj = await space_service.get_space_by_id(session, sp["id"])
        result.append({
            "id": str(sp["id"]),
            "name": sp["name"],
            "role": sp["role"],
            "member_count": sp["member_count"],
            "invite_code": space_obj.invite_code if space_obj else None,
        })

    return web.json_response(result)


@routes.post("/api/spaces")
async def create_space(request: web.Request) -> web.Response:
    """Создание нового пространства."""
    user_id: int = request["user_id"]
    session = request["session"]

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Невалидное тело запроса"}, status=400)

    name = body.get("name")
    if name is None:
        return web.json_response({"error": "Поле name обязательно"}, status=400)

    name = str(name).strip()
    if not name:
        return web.json_response({"error": "Название не может быть пустым"}, status=400)
    if len(name) > 255:
        return web.json_response({"error": "Название слишком длинное (макс. 255 символов)"}, status=400)

    space = await space_service.create_space(session, user_id, name)

    return web.json_response({
        "id": str(space.id),
        "name": space.name,
        "invite_code": space.invite_code,
        "role": "admin",
        "member_count": 1,
    }, status=201)


@routes.get("/api/spaces/{space_id}")
async def get_space(request: web.Request) -> web.Response:
    """Информация о пространстве и список участников."""
    user_id: int = request["user_id"]
    session = request["session"]

    try:
        space_id = UUID(request.match_info["space_id"])
    except ValueError:
        return web.json_response({"error": "Невалидный space_id"}, status=400)

    # Проверяем членство
    from app.db.models import UserSpace

    membership = await session.get(UserSpace, (user_id, space_id))
    if membership is None:
        return web.json_response({"error": "Нет доступа к пространству"}, status=403)

    space = await space_service.get_space_by_id(session, space_id)
    if space is None:
        return web.json_response({"error": "Пространство не найдено"}, status=404)

    members = await space_service.get_space_members(session, space_id)

    return web.json_response({
        "id": str(space.id),
        "name": space.name,
        "invite_code": space.invite_code,
        "created_by": space.created_by,
        "members": [
            {
                "user_id": m["user_id"],
                "first_name": m["first_name"],
                "username": m["username"],
                "role": m["role"],
                "joined_at": m.get("joined_at"),
            }
            for m in members
        ],
    })


@routes.put("/api/spaces/{space_id}")
async def update_space(request: web.Request) -> web.Response:
    """Обновление названия пространства. Только для администратора."""
    user_id: int = request["user_id"]
    session = request["session"]

    try:
        space_id = UUID(request.match_info["space_id"])
    except ValueError:
        return web.json_response({"error": "Невалидный space_id"}, status=400)

    is_admin = await space_service.check_admin(session, space_id, user_id)
    if not is_admin:
        return web.json_response({"error": "Только администратор может редактировать пространство"}, status=403)

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Невалидное тело запроса"}, status=400)

    name = body.get("name", "").strip()
    if not name or len(name) > 255:
        return web.json_response({"error": "Название должно быть от 1 до 255 символов"}, status=400)

    space = await space_service.update_space_name(session, space_id, name)
    if space is None:
        return web.json_response({"error": "Пространство не найдено"}, status=404)

    members = await space_service.get_space_members(session, space_id)

    return web.json_response({
        "id": str(space.id),
        "name": space.name,
        "invite_code": space.invite_code,
        "created_by": space.created_by,
        "members": [
            {
                "user_id": m["user_id"],
                "first_name": m["first_name"],
                "username": m["username"],
                "role": m["role"],
                "joined_at": m.get("joined_at"),
            }
            for m in members
        ],
    })


@routes.delete("/api/spaces/{space_id}")
async def delete_space(request: web.Request) -> web.Response:
    """Удаление пространства. Только для администратора."""
    user_id: int = request["user_id"]
    session = request["session"]

    try:
        space_id = UUID(request.match_info["space_id"])
    except ValueError:
        return web.json_response({"error": "Невалидный space_id"}, status=400)

    is_admin = await space_service.check_admin(session, space_id, user_id)
    if not is_admin:
        return web.json_response({"error": "Только администратор может удалить пространство"}, status=403)

    # Собираем данные до каскадного удаления
    space = await space_service.get_space_by_id(session, space_id)
    space_name = space.name if space else "Неизвестное"
    members = await space_service.get_space_members(session, space_id)
    admin_user = await session.get(User, user_id)
    admin_name = admin_user.first_name if admin_user else "Неизвестный"

    await space_service.delete_space(session, space_id)
    await session.commit()

    # Уведомляем участников (fire-and-forget, после commit)
    bot = request.app.get("bot")
    if bot and members:
        for member in members:
            if member["user_id"] == user_id:
                continue
            try:
                member_user = await session.get(User, member["user_id"])
                member_lang = member_user.language if member_user else "en"
                notification = format_space_deleted_notification(
                    space_name, admin_name, lang=member_lang,
                )
                await bot.send_message(member["user_id"], notification)
            except Exception as e:
                logger.warning(
                    "Не удалось уведомить об удалении пространства: user_id=%s space_id=%s error=%s",
                    member["user_id"],
                    space_id,
                    e,
                )

    return web.Response(status=204)


@routes.delete("/api/spaces/{space_id}/members/{member_user_id}")
async def kick_member(request: web.Request) -> web.Response:
    """Исключение участника из пространства. Только для администратора."""
    user_id: int = request["user_id"]
    session = request["session"]

    try:
        space_id = UUID(request.match_info["space_id"])
        member_user_id = int(request.match_info["member_user_id"])
    except (ValueError, KeyError):
        return web.json_response({"error": "Невалидные параметры"}, status=400)

    # Нельзя кикнуть самого себя
    if member_user_id == user_id:
        return web.json_response({"error": "Нельзя исключить самого себя"}, status=400)

    is_admin = await space_service.check_admin(session, space_id, user_id)
    if not is_admin:
        return web.json_response({"error": "Только администратор может исключать участников"}, status=403)

    await space_service.kick_member(session, space_id, member_user_id)
    return web.Response(status=204)
