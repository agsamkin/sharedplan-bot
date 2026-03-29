"""API-маршруты для работы с событиями (events).

Эндпоинты:
- GET /api/spaces/{space_id}/events — список ближайших событий пространства
- POST /api/spaces/{space_id}/events — создание события в пространстве
- GET /api/events/{event_id} — информация о событии
- PUT /api/events/{event_id} — редактирование события (только владелец)
- DELETE /api/events/{event_id} — удаление события (только владелец)
"""

import logging
from datetime import date, time
from uuid import UUID

from aiohttp import web
from sqlalchemy import select

from app.bot.formatting import (
    format_date_short_with_weekday,
    format_event_deleted_notification,
    format_event_edited_notification,
)
from app.db.models import Event, Space, User, UserSpace
from app.services import event_service, reminder_service

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


def _serialize_event(event: Event, creator_name: str | None = None, is_owner: bool = False) -> dict:
    """Сериализация события в словарь для JSON-ответа."""
    return {
        "id": str(event.id),
        "title": event.title,
        "event_date": str(event.event_date),
        "event_time": event.event_time.strftime("%H:%M") if event.event_time else None,
        "created_by": event.created_by,
        "creator_name": creator_name,
        "is_owner": is_owner,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


@routes.get("/api/spaces/{space_id}/events")
async def list_events(request: web.Request) -> web.Response:
    """Список ближайших будущих событий пространства."""
    user_id: int = request["user_id"]
    session = request["session"]

    try:
        space_id = UUID(request.match_info["space_id"])
    except ValueError:
        return web.json_response({"error": "Невалидный space_id"}, status=400)

    # Парсим limit из query (default=50, max=100, min=1)
    try:
        limit = int(request.query.get("limit", "50"))
    except (ValueError, TypeError):
        limit = 50
    limit = max(1, min(limit, 100))

    # Проверяем членство
    membership = await session.get(UserSpace, (user_id, space_id))
    if membership is None:
        return web.json_response({"error": "Нет доступа к пространству"}, status=403)

    events = await event_service.get_upcoming_events(session, space_id, limit=limit)
    total_count = await event_service.count_upcoming_events(session, space_id)

    logger.info(
        "list_events user_id=%d space_id=%s returned=%d total_count=%d",
        user_id, space_id, len(events), total_count,
    )

    # Собираем имена создателей
    creator_ids = {e.created_by for e in events}
    creators = {}
    for cid in creator_ids:
        user = await session.get(User, cid)
        if user:
            creators[cid] = user.first_name

    result = [
        _serialize_event(
            e,
            creator_name=creators.get(e.created_by),
            is_owner=(e.created_by == user_id),
        )
        for e in events
    ]

    return web.json_response({"events": result, "total_count": total_count})


@routes.post("/api/spaces/{space_id}/events")
async def create_event(request: web.Request) -> web.Response:
    """Создание события в пространстве.

    Принимает JSON body: title (обязательно), event_date (обязательно), event_time (опционально).
    Создаёт напоминания для участников и отправляет уведомления.
    """
    user_id: int = request["user_id"]
    session = request["session"]

    try:
        space_id = UUID(request.match_info["space_id"])
    except ValueError:
        return web.json_response({"error": "Невалидный space_id"}, status=400)

    # Проверяем членство
    membership = await session.get(UserSpace, (user_id, space_id))
    if membership is None:
        return web.json_response({"error": "Нет доступа к пространству"}, status=403)

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Невалидный JSON"}, status=400)

    # Валидация title
    title = body.get("title")
    if title is None:
        return web.json_response({"error": "Поле title обязательно"}, status=400)
    if not isinstance(title, str) or not title.strip():
        return web.json_response({"error": "Название не может быть пустым"}, status=400)
    if len(title.strip()) > 500:
        return web.json_response({"error": "Название слишком длинное (макс. 500 символов)"}, status=400)

    # Валидация event_date
    raw_date = body.get("event_date")
    if raw_date is None:
        return web.json_response({"error": "Поле event_date обязательно"}, status=400)
    try:
        event_date = date.fromisoformat(raw_date)
    except (ValueError, TypeError):
        return web.json_response({"error": "Невалидный формат даты"}, status=400)

    # Валидация event_time (опционально)
    event_time = None
    raw_time = body.get("event_time")
    if raw_time is not None:
        try:
            parts = raw_time.split(":")
            event_time = time(int(parts[0]), int(parts[1]))
        except (ValueError, TypeError, IndexError, AttributeError):
            return web.json_response({"error": "Невалидный формат времени (ожидается HH:MM)"}, status=400)

    # Создаём событие
    event = await event_service.create_event(
        session,
        space_id=space_id,
        title=title.strip(),
        event_date=event_date,
        event_time=event_time,
        created_by=user_id,
        raw_input=None,
    )

    # Создаём напоминания для участников
    await reminder_service.create_reminders_for_event(session, event, space_id)

    # Уведомляем участников
    creator = await session.get(User, user_id)
    creator_name = creator.first_name if creator else None

    space = await session.get(Space, space_id)
    space_name = space.name if space else ""

    notification_lines = [
        f"📅 Новое событие в «{space_name}»!\n",
        f"📝 {event.title}",
        f"📅 {event.event_date}",
    ]
    if event.event_time:
        notification_lines.append(f"⏰ {event.event_time.strftime('%H:%M')}")
    notification_lines.append(f"👤 Добавил: {creator_name or 'Неизвестный'}")

    await _notify_space_members(
        request, session, space_id, user_id,
        "\n".join(notification_lines),
    )

    result = _serialize_event(event, creator_name=creator_name, is_owner=True)
    return web.json_response(result, status=201)


@routes.get("/api/events/{event_id}")
async def get_event(request: web.Request) -> web.Response:
    """Информация о конкретном событии с данными пространства."""
    user_id: int = request["user_id"]
    session = request["session"]

    try:
        event_id = UUID(request.match_info["event_id"])
    except ValueError:
        return web.json_response({"error": "Невалидный event_id"}, status=400)

    event = await session.get(Event, event_id)
    if event is None:
        return web.json_response({"error": "Событие не найдено"}, status=404)

    # Проверяем членство в пространстве события
    membership = await session.get(UserSpace, (user_id, event.space_id))
    if membership is None:
        return web.json_response({"error": "Нет доступа к событию"}, status=403)

    # Данные создателя
    creator = await session.get(User, event.created_by)
    creator_name = creator.first_name if creator else None

    # Данные пространства
    space = await session.get(Space, event.space_id)

    result = _serialize_event(event, creator_name=creator_name, is_owner=(event.created_by == user_id))
    result["space_id"] = str(event.space_id)
    result["space_name"] = space.name if space else None

    return web.json_response(result)


@routes.put("/api/events/{event_id}")
async def update_event(request: web.Request) -> web.Response:
    """Редактирование события. Только владелец может редактировать.

    Принимает JSON body с опциональными полями: title, event_date, event_time.
    При изменении даты/времени пересоздаёт напоминания.
    Уведомляет участников пространства об изменении.
    """
    user_id: int = request["user_id"]
    session = request["session"]

    try:
        event_id = UUID(request.match_info["event_id"])
    except ValueError:
        return web.json_response({"error": "Невалидный event_id"}, status=400)

    # Проверяем, что пользователь — владелец события
    event = await event_service.get_event_for_owner(session, event_id, user_id)
    if event is None:
        # Проверяем, существует ли событие вообще
        existing = await session.get(Event, event_id)
        if existing is None:
            return web.json_response({"error": "Событие не найдено"}, status=404)
        return web.json_response({"error": "Только владелец может редактировать событие"}, status=403)

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Невалидный JSON"}, status=400)

    # Собираем поля для обновления
    update_fields = {}
    date_time_changed = False

    if "title" in body:
        title = body["title"]
        if not isinstance(title, str) or not title.strip():
            return web.json_response({"error": "Название не может быть пустым"}, status=400)
        if len(title.strip()) > 500:
            return web.json_response({"error": "Название слишком длинное (макс. 500 символов)"}, status=400)
        update_fields["title"] = title.strip()

    if "event_date" in body:
        try:
            update_fields["event_date"] = date.fromisoformat(body["event_date"])
            date_time_changed = True
        except (ValueError, TypeError):
            return web.json_response({"error": "Невалидный формат event_date (ожидается YYYY-MM-DD)"}, status=400)

    if "event_time" in body:
        if body["event_time"] is None:
            update_fields["event_time"] = None
            date_time_changed = True
        else:
            try:
                parts = body["event_time"].split(":")
                update_fields["event_time"] = time(int(parts[0]), int(parts[1]))
                date_time_changed = True
            except (ValueError, TypeError, IndexError, AttributeError):
                return web.json_response({"error": "Невалидный формат event_time (ожидается HH:MM)"}, status=400)

    if not update_fields:
        return web.json_response({"error": "Нет полей для обновления"}, status=400)

    # Сохраняем старые значения ДО обновления для формирования уведомления
    old_title = event.title
    old_event_date = event.event_date
    old_event_time = event.event_time

    # Обновляем событие
    updated_event = await event_service.update_event(session, event_id, **update_fields)

    # Пересоздаём напоминания, если изменилась дата/время
    if date_time_changed and updated_event:
        await reminder_service.recreate_reminders_for_event(session, updated_event, updated_event.space_id)

    # Уведомляем участников пространства с детальным описанием изменений
    if updated_event:
        # Собираем список изменений (field_label, old_formatted, new_formatted)
        changes: list[tuple[str, str, str]] = []

        if "title" in update_fields and update_fields["title"] != old_title:
            changes.append(("Название", old_title, update_fields["title"]))

        if "event_date" in update_fields and update_fields["event_date"] != old_event_date:
            changes.append((
                "Дата",
                format_date_short_with_weekday(old_event_date),
                format_date_short_with_weekday(update_fields["event_date"]),
            ))

        if "event_time" in update_fields and update_fields["event_time"] != old_event_time:
            old_time_str = old_event_time.strftime("%H:%M") if old_event_time else "весь день"
            new_time_str = update_fields["event_time"].strftime("%H:%M") if update_fields["event_time"] else "весь день"
            changes.append(("Время", old_time_str, new_time_str))

        if changes:
            # Получаем название пространства и имя редактора
            space = await session.get(Space, updated_event.space_id)
            space_name = space.name if space else ""
            editor = await session.get(User, user_id)
            editor_name = editor.first_name if editor else "Неизвестный"

            notification_text = format_event_edited_notification(
                space_name=space_name,
                title=updated_event.title,
                changes=changes,
                editor_name=editor_name,
            )
            await _notify_space_members(
                request, session, updated_event.space_id, user_id,
                notification_text,
            )

    # Проверяем конфликты при изменении даты/времени
    conflicts_data = []
    if date_time_changed and updated_event and updated_event.event_time is not None:
        conflicts = await event_service.find_conflicting_events(
            session,
            updated_event.space_id,
            updated_event.event_date,
            updated_event.event_time,
            exclude_event_id=event_id,
        )
        for c in conflicts:
            conflicts_data.append({
                "id": str(c.id),
                "title": c.title,
                "event_time": c.event_time.strftime("%H:%M") if c.event_time else None,
            })

    # Получаем имя создателя для ответа
    creator = await session.get(User, user_id)
    creator_name = creator.first_name if creator else None

    result = _serialize_event(updated_event, creator_name=creator_name, is_owner=True)
    if conflicts_data:
        result["conflicts"] = conflicts_data
    return web.json_response(result)


@routes.delete("/api/events/{event_id}")
async def delete_event(request: web.Request) -> web.Response:
    """Удаление события. Только владелец может удалить.

    Уведомляет участников пространства перед удалением.
    """
    user_id: int = request["user_id"]
    session = request["session"]

    try:
        event_id = UUID(request.match_info["event_id"])
    except ValueError:
        return web.json_response({"error": "Невалидный event_id"}, status=400)

    # Проверяем, что пользователь — владелец события
    event = await event_service.get_event_for_owner(session, event_id, user_id)
    if event is None:
        existing = await session.get(Event, event_id)
        if existing is None:
            return web.json_response({"error": "Событие не найдено"}, status=404)
        return web.json_response({"error": "Только владелец может удалить событие"}, status=403)

    # Получаем название пространства и имя удалившего для уведомления
    space = await session.get(Space, event.space_id)
    space_name = space.name if space else ""
    editor = await session.get(User, user_id)
    editor_name = editor.first_name if editor else "Неизвестный"

    # Уведомляем участников ДО удаления
    notification_text = format_event_deleted_notification(
        space_name=space_name,
        title=event.title,
        editor_name=editor_name,
        event_date=event.event_date,
        event_time=event.event_time,
    )
    await _notify_space_members(
        request,
        session,
        event.space_id,
        user_id,
        notification_text,
    )

    await event_service.delete_event(session, event_id)
    return web.Response(status=204)


async def _notify_space_members(
    request: web.Request,
    session,
    space_id: UUID,
    exclude_user_id: int,
    message: str,
) -> None:
    """Отправить уведомление всем участникам пространства, кроме указанного.

    Ошибки при отправке отдельному участнику не прерывают процесс.
    """
    bot = request.app.get("bot")
    if bot is None:
        logger.warning("Бот не доступен для отправки уведомлений")
        return

    # Получаем участников пространства
    stmt = select(UserSpace.user_id).where(UserSpace.space_id == space_id)
    result = await session.execute(stmt)
    member_ids = [row.user_id for row in result.all()]

    for member_id in member_ids:
        if member_id == exclude_user_id:
            continue
        try:
            await bot.send_message(member_id, message)
        except Exception as e:
            logger.warning(
                "Не удалось отправить уведомление пользователю %d: %s",
                member_id, e,
            )
