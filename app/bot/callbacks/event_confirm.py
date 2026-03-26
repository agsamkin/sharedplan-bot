import logging
from datetime import date, time
from uuid import UUID

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.not_command import NotCommandFilter
from app.bot.formatting import FORMAT_HINT, format_confirmation, format_notification
from app.bot.keyboards.confirm import event_confirm_keyboard
from app.bot.states.create_event import CreateEvent
from app.services import event_service, space_service
from app.services.event_service import parse_event_text

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "event_confirm")
async def on_event_confirm(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
) -> None:
    data = await state.get_data()
    if not data.get("parsed_title"):
        await callback.answer("Нет данных события")
        return

    space_id = UUID(data["space_id"])
    event_date = date.fromisoformat(data["parsed_date"])
    event_time = time.fromisoformat(data["parsed_time"]) if data.get("parsed_time") else None

    await event_service.create_event(
        session=session,
        space_id=space_id,
        title=data["parsed_title"],
        event_date=event_date,
        event_time=event_time,
        created_by=callback.from_user.id,
        raw_input=data.get("raw_input"),
    )

    await callback.message.edit_text("✅ Событие опубликовано!")
    await state.clear()

    # Уведомление участников
    space = await space_service.get_space_by_id(session, space_id)
    space_name = space.name if space else "Неизвестное"
    members = await space_service.get_space_members(session, space_id)
    creator_name = callback.from_user.first_name

    notification = format_notification(
        space_name, data["parsed_title"], event_date, event_time, creator_name,
    )

    for member in members:
        if member["user_id"] == callback.from_user.id:
            continue
        try:
            await bot.send_message(member["user_id"], notification)
        except Exception:
            logger.warning(
                "Не удалось отправить уведомление пользователю %s",
                member["user_id"],
            )

    await callback.answer()


@router.callback_query(F.data == "event_cancel")
async def on_event_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("❌ Создание события отменено.")
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "event_edit")
async def on_event_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CreateEvent.waiting_for_edit)
    await callback.message.edit_text(
        f"Отправь исправленный вариант.\n\n{FORMAT_HINT}"
    )
    await callback.answer()


@router.message(CreateEvent.waiting_for_edit, NotCommandFilter())
async def handle_event_edit(
    message: Message, state: FSMContext, session: AsyncSession,
) -> None:
    """Повторный ввод после нажатия «Изменить»."""
    try:
        parsed = await parse_event_text(message.text)
    except ValueError as e:
        await message.answer(f"❌ {e}\n\n{FORMAT_HINT}")
        return

    await state.update_data(
        parsed_title=parsed.title,
        parsed_date=parsed.date.isoformat(),
        parsed_time=parsed.time.strftime("%H:%M") if parsed.time else None,
        raw_input=message.text,
    )
    await state.set_state(CreateEvent.waiting_for_confirm)

    await message.answer(
        format_confirmation(parsed.title, parsed.date, parsed.time),
        reply_markup=event_confirm_keyboard(),
    )
