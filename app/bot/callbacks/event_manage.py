import logging
from datetime import date, time
from uuid import UUID

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.not_command import NotCommandFilter
from app.bot.formatting import (
    PARSE_ERROR_MESSAGES,
    format_date_with_weekday,
    format_event_deleted_notification,
    format_event_edited_notification,
    format_event_manage_card,
)
from app.bot.keyboards.event_manage import (
    event_delete_confirm_keyboard,
    event_edit_confirm_keyboard,
    event_edit_field_keyboard,
    event_edit_time_keyboard,
    event_manage_keyboard,
)
from app.bot.states.edit_event import EditEvent
from app.services import event_service, reminder_service, space_service
from app.services.llm_parser import ParseError, parse_event

logger = logging.getLogger(__name__)
router = Router()


# --- Карточка управления ---

@router.callback_query(F.data.startswith("event_manage:"))
async def on_event_manage(
    callback: CallbackQuery, session: AsyncSession,
) -> None:
    event_id = UUID(callback.data.split(":", 1)[1])
    event = await event_service.get_event_for_owner(
        session, event_id, callback.from_user.id,
    )
    if not event:
        await callback.answer("Событие не найдено", show_alert=True)
        return

    text = format_event_manage_card(event.title, event.event_date, event.event_time)
    await callback.message.edit_text(text, reply_markup=event_manage_keyboard(event_id))
    await callback.answer()


# --- Удаление ---
# NB: event_delete_yes/no MUST be registered BEFORE event_delete
# because "event_delete_yes:".startswith("event_delete:") is True.

@router.callback_query(F.data.startswith("event_delete_yes:"))
async def on_event_delete_yes(
    callback: CallbackQuery, session: AsyncSession, bot: Bot,
) -> None:
    event_id = UUID(callback.data.split(":", 1)[1])
    event = await event_service.get_event_for_owner(
        session, event_id, callback.from_user.id,
    )
    if not event:
        await callback.answer("Событие не найдено", show_alert=True)
        return

    title = event.title
    space_id = event.space_id

    await event_service.delete_event(session, event_id)
    await callback.message.edit_text("✅ Событие удалено.")
    await callback.answer()

    # Уведомления участников
    space = await space_service.get_space_by_id(session, space_id)
    space_name = space.name if space else "Неизвестное"
    notification = format_event_deleted_notification(
        space_name, title, callback.from_user.first_name,
    )
    members = await space_service.get_space_members(session, space_id)
    for member in members:
        if member["user_id"] == callback.from_user.id:
            continue
        try:
            await bot.send_message(member["user_id"], notification)
        except Exception as e:
            logger.warning(
                "Не удалось отправить уведомление об удалении: user_id=%s error=%s",
                member["user_id"], e,
            )


@router.callback_query(F.data.startswith("event_delete_no:"))
async def on_event_delete_no(
    callback: CallbackQuery, session: AsyncSession,
) -> None:
    event_id = UUID(callback.data.split(":", 1)[1])
    event = await event_service.get_event_for_owner(
        session, event_id, callback.from_user.id,
    )
    if not event:
        await callback.answer("Событие не найдено", show_alert=True)
        return

    text = format_event_manage_card(event.title, event.event_date, event.event_time)
    await callback.message.edit_text(text, reply_markup=event_manage_keyboard(event_id))
    await callback.answer()


@router.callback_query(F.data.startswith("event_delete:"))
async def on_event_delete(
    callback: CallbackQuery, session: AsyncSession,
) -> None:
    event_id = UUID(callback.data.split(":", 1)[1])
    event = await event_service.get_event_for_owner(
        session, event_id, callback.from_user.id,
    )
    if not event:
        await callback.answer("Событие не найдено", show_alert=True)
        return

    await callback.message.edit_text(
        f"Удалить событие «{event.title}»?\nЭто действие нельзя отменить.",
        reply_markup=event_delete_confirm_keyboard(event_id),
    )
    await callback.answer()


# --- Редактирование: выбор поля ---

@router.callback_query(F.data.startswith("event_edit_field:"))
async def on_event_edit_field(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext,
) -> None:
    parts = callback.data.split(":")
    event_id = UUID(parts[1])
    field = parts[2]  # "choose", "title", "date", "time"

    event = await event_service.get_event_for_owner(
        session, event_id, callback.from_user.id,
    )
    if not event:
        await callback.answer("Событие не найдено", show_alert=True)
        return

    if field == "choose":
        await callback.message.edit_text(
            f"Что изменить в событии «{event.title}»?",
            reply_markup=event_edit_field_keyboard(event_id),
        )
        await callback.answer()
        return

    # Сохраняем контекст редактирования в FSM
    await state.update_data(
        edit_event_id=str(event_id),
        edit_field=field,
        edit_old_title=event.title,
        edit_old_date=event.event_date.isoformat(),
        edit_old_time=event.event_time.strftime("%H:%M") if event.event_time else None,
        edit_space_id=str(event.space_id),
    )

    if field == "title":
        await state.set_state(EditEvent.waiting_for_value)
        await callback.message.edit_text(
            f"Текущее название: «{event.title}»\n\nОтправь новое название:"
        )
    elif field == "date":
        await state.set_state(EditEvent.waiting_for_value)
        await callback.message.edit_text(
            f"Текущая дата: {format_date_with_weekday(event.event_date)}\n\n"
            "Отправь новую дату (например: «завтра», «5 апреля», «15.04»):"
        )
    elif field == "time":
        time_str = event.event_time.strftime("%H:%M") if event.event_time else "не указано"
        await state.set_state(EditEvent.waiting_for_value)
        await callback.message.edit_text(
            f"Текущее время: {time_str}\n\n"
            "Отправь новое время (например: «15:30», «в 8 вечера»)\n"
            "или нажми кнопку ниже, чтобы убрать время:",
            reply_markup=event_edit_time_keyboard(event_id),
        )

    await callback.answer()


# --- Редактирование: ввод нового значения ---

@router.message(EditEvent.waiting_for_value, NotCommandFilter())
async def handle_edit_value(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot,
) -> None:
    data = await state.get_data()
    field = data["edit_field"]
    text = (message.text or "").strip()

    if not text:
        return

    if field == "title":
        if len(text) > 500:
            await message.answer("❌ Название слишком длинное (максимум 500 символов). Попробуй короче:")
            return

        await state.update_data(edit_new_value=text)
        await state.set_state(EditEvent.waiting_for_confirm)
        await message.answer(
            f"Изменить название?\n\n"
            f"Было: «{data['edit_old_title']}»\n"
            f"Станет: «{text}»",
            reply_markup=event_edit_confirm_keyboard(),
        )

    elif field == "date":
        await bot.send_chat_action(message.chat.id, "typing")
        try:
            parsed = await parse_event(f"Событие {text}")
        except ParseError as e:
            await message.answer(
                f"❌ {PARSE_ERROR_MESSAGES.get(e.error_type, 'Не удалось распознать дату.')} Попробуй ещё раз:"
            )
            return

        new_date = parsed.event_date
        old_date = date.fromisoformat(data["edit_old_date"])
        await state.update_data(edit_new_value=new_date.isoformat())
        await state.set_state(EditEvent.waiting_for_confirm)
        await message.answer(
            f"Изменить дату?\n\n"
            f"Было: {format_date_with_weekday(old_date)}\n"
            f"Станет: {format_date_with_weekday(new_date)}",
            reply_markup=event_edit_confirm_keyboard(),
        )

    elif field == "time":
        await bot.send_chat_action(message.chat.id, "typing")
        try:
            parsed = await parse_event(f"Событие сегодня {text}")
        except ParseError as e:
            await message.answer(
                f"❌ {PARSE_ERROR_MESSAGES.get(e.error_type, 'Не удалось распознать время.')} Попробуй ещё раз:"
            )
            return

        if parsed.event_time is None:
            await message.answer("❌ Не удалось определить время. Попробуй формат «15:30» или «в 8 вечера»:")
            return

        new_time = parsed.event_time
        old_time_str = data["edit_old_time"] or "не указано"
        await state.update_data(edit_new_value=new_time.strftime("%H:%M"))
        await state.set_state(EditEvent.waiting_for_confirm)
        await message.answer(
            f"Изменить время?\n\n"
            f"Было: {old_time_str}\n"
            f"Станет: {new_time.strftime('%H:%M')}",
            reply_markup=event_edit_confirm_keyboard(),
        )


# --- Убрать время ---

@router.callback_query(F.data.startswith("event_remove_time:"))
async def on_event_remove_time(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext, bot: Bot,
) -> None:
    event_id = UUID(callback.data.split(":", 1)[1])
    event = await event_service.get_event_for_owner(
        session, event_id, callback.from_user.id,
    )
    if not event:
        await callback.answer("Событие не найдено", show_alert=True)
        return

    old_time_str = event.event_time.strftime("%H:%M") if event.event_time else "не указано"

    await event_service.update_event(session, event_id, event_time=None)
    # Перечитываем событие после обновления
    event = await session.get(event_service.Event, event_id)
    await reminder_service.recreate_reminders_for_event(session, event, event.space_id)
    await state.clear()

    await callback.message.edit_text("✅ Время убрано. Событие теперь на весь день.")
    await callback.answer()

    # Уведомления
    space = await space_service.get_space_by_id(session, event.space_id)
    space_name = space.name if space else "Неизвестное"
    notification = format_event_edited_notification(
        space_name, event.title, "Время", old_time_str, "весь день",
        callback.from_user.first_name,
    )
    members = await space_service.get_space_members(session, event.space_id)
    for member in members:
        if member["user_id"] == callback.from_user.id:
            continue
        try:
            await bot.send_message(member["user_id"], notification)
        except Exception as e:
            logger.warning(
                "Не удалось отправить уведомление: user_id=%s error=%s",
                member["user_id"], e,
            )


# --- Подтверждение/отмена редактирования ---

@router.callback_query(F.data == "event_edit_confirm")
async def on_event_edit_confirm(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot,
) -> None:
    data = await state.get_data()
    event_id = UUID(data["edit_event_id"])
    field = data["edit_field"]
    new_value = data["edit_new_value"]

    event = await event_service.get_event_for_owner(
        session, event_id, callback.from_user.id,
    )
    if not event:
        await callback.answer("Событие не найдено", show_alert=True)
        await state.clear()
        return

    # Определяем старое и новое значение для уведомления
    if field == "title":
        old_display = data["edit_old_title"]
        new_display = new_value
        field_label = "Название"
        await event_service.update_event(session, event_id, title=new_value)
    elif field == "date":
        old_date = date.fromisoformat(data["edit_old_date"])
        new_date = date.fromisoformat(new_value)
        old_display = format_date_with_weekday(old_date)
        new_display = format_date_with_weekday(new_date)
        field_label = "Дата"
        await event_service.update_event(session, event_id, event_date=new_date)
        event = await session.get(event_service.Event, event_id)
        await reminder_service.recreate_reminders_for_event(session, event, event.space_id)
    elif field == "time":
        old_display = data["edit_old_time"] or "не указано"
        new_time = time.fromisoformat(new_value)
        new_display = new_time.strftime("%H:%M")
        field_label = "Время"
        await event_service.update_event(session, event_id, event_time=new_time)
        event = await session.get(event_service.Event, event_id)
        await reminder_service.recreate_reminders_for_event(session, event, event.space_id)

    await state.clear()
    await callback.message.edit_text("✅ Событие обновлено!")
    await callback.answer()

    # Уведомления участников
    space_id = UUID(data["edit_space_id"])
    space = await space_service.get_space_by_id(session, space_id)
    space_name = space.name if space else "Неизвестное"
    title = new_value if field == "title" else data["edit_old_title"]
    notification = format_event_edited_notification(
        space_name, title, field_label, old_display, new_display,
        callback.from_user.first_name,
    )
    members = await space_service.get_space_members(session, space_id)
    for member in members:
        if member["user_id"] == callback.from_user.id:
            continue
        try:
            await bot.send_message(member["user_id"], notification)
        except Exception as e:
            logger.warning(
                "Не удалось отправить уведомление: user_id=%s error=%s",
                member["user_id"], e,
            )


@router.callback_query(F.data == "event_edit_cancel")
async def on_event_edit_cancel(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession,
) -> None:
    data = await state.get_data()
    event_id = UUID(data["edit_event_id"])

    event = await event_service.get_event_for_owner(
        session, event_id, callback.from_user.id,
    )
    await state.clear()

    if event:
        text = format_event_manage_card(event.title, event.event_date, event.event_time)
        await callback.message.edit_text(text, reply_markup=event_manage_keyboard(event_id))
    else:
        await callback.message.edit_text("Редактирование отменено.")
    await callback.answer()
