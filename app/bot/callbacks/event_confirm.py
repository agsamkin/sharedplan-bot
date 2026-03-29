import logging
from datetime import date, time
from uuid import UUID

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.not_command import NotCommandFilter
from app.bot.formatting import (
    format_confirmation,
    format_conflict_warning,
    format_notification,
    get_parse_error_message,
)
from app.bot.keyboards.confirm import event_confirm_keyboard
from app.bot.states.create_event import CreateEvent
from app.i18n import t
from app.services import event_service, reminder_service, space_service
from app.services.llm_parser import ParseError, parse_event

# Re-exports for registration
__all__ = ["router"]

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "event_confirm")
async def on_event_confirm(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
    lang: str = "en",
) -> None:
    data = await state.get_data()
    lang = data.get("lang", lang)

    if not data.get("parsed_title"):
        await callback.answer(t(lang, "cb.confirm.no_data"))
        return

    space_id = UUID(data["space_id"])
    event_date = date.fromisoformat(data["parsed_date"])
    event_time = time.fromisoformat(data["parsed_time"]) if data.get("parsed_time") else None

    event = await event_service.create_event(
        session=session,
        space_id=space_id,
        title=data["parsed_title"],
        event_date=event_date,
        event_time=event_time,
        created_by=callback.from_user.id,
        raw_input=data.get("raw_input"),
    )

    await reminder_service.create_reminders_for_event(session, event, space_id)

    await callback.message.edit_text(t(lang, "cb.confirm.published"))
    await state.clear()

    # Уведомление участников
    space = await space_service.get_space_by_id(session, space_id)
    space_name = space.name if space else "Unknown"
    members = await space_service.get_space_members(session, space_id)
    creator_name = callback.from_user.first_name

    notification = format_notification(
        space_name, data["parsed_title"], event_date, event_time, creator_name,
        lang=lang,
    )

    for member in members:
        if member["user_id"] == callback.from_user.id:
            continue
        try:
            await bot.send_message(member["user_id"], notification)
        except Exception as e:
            logger.warning(
                "Не удалось отправить уведомление: user_id=%s error_type=%s error=%s",
                member["user_id"],
                type(e).__name__,
                e,
            )

    await callback.answer()


@router.callback_query(F.data == "event_cancel")
async def on_event_cancel(
    callback: CallbackQuery, state: FSMContext, lang: str = "en",
) -> None:
    await callback.message.edit_text(t(lang, "cb.confirm.cancelled"))
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "event_edit")
async def on_event_edit(
    callback: CallbackQuery, state: FSMContext, lang: str = "en",
) -> None:
    await state.set_state(CreateEvent.waiting_for_edit)
    await callback.message.edit_text(t(lang, "cb.confirm.edit_prompt"))
    await callback.answer()


@router.message(CreateEvent.waiting_for_edit, NotCommandFilter())
async def handle_event_edit(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot,
    lang: str = "en",
) -> None:
    """Повторный ввод после нажатия «Изменить»."""
    data = await state.get_data()
    lang = data.get("lang", lang)

    await bot.send_chat_action(message.chat.id, "typing")

    try:
        parsed = await parse_event(message.text)
    except ParseError as e:
        await message.answer(f"\u274c {get_parse_error_message(lang, e.error_type)}")
        # Остаёмся в waiting_for_edit — пользователь может попробовать снова
        await state.set_state(CreateEvent.waiting_for_edit)
        return

    await state.update_data(
        parsed_title=parsed.title,
        parsed_date=parsed.event_date.isoformat(),
        parsed_time=parsed.event_time.strftime("%H:%M") if parsed.event_time else None,
        raw_input=message.text,
        transcript=None,
    )

    conflict_warning = None
    if parsed.event_time is not None and data.get("space_id"):
        conflicts = await event_service.find_conflicting_events(
            session, UUID(data["space_id"]), parsed.event_date, parsed.event_time,
        )
        if conflicts:
            conflict_warning = format_conflict_warning(conflicts, lang)

    await state.set_state(CreateEvent.waiting_for_confirm)

    await message.answer(
        format_confirmation(
            parsed.title, parsed.event_date, parsed.event_time,
            conflict_warning=conflict_warning, lang=lang,
        ),
        reply_markup=event_confirm_keyboard(lang),
    )


@router.callback_query(F.data == "event_past_confirm")
async def on_event_past_confirm(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession,
    lang: str = "en",
) -> None:
    """Пользователь подтвердил создание события с прошедшей датой."""
    data = await state.get_data()
    lang = data.get("lang", lang)

    if not data.get("parsed_title"):
        await callback.answer(t(lang, "cb.confirm.no_data"))
        return

    event_date = date.fromisoformat(data["parsed_date"])
    event_time = time.fromisoformat(data["parsed_time"]) if data.get("parsed_time") else None
    transcript = data.get("transcript")

    conflict_warning = None
    if event_time is not None and data.get("space_id"):
        conflicts = await event_service.find_conflicting_events(
            session, UUID(data["space_id"]), event_date, event_time,
        )
        if conflicts:
            conflict_warning = format_conflict_warning(conflicts, lang)

    await state.set_state(CreateEvent.waiting_for_confirm)
    await callback.message.edit_text(
        format_confirmation(
            data["parsed_title"], event_date, event_time,
            transcript=transcript, conflict_warning=conflict_warning,
            lang=lang,
        ),
        reply_markup=event_confirm_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "event_past_cancel")
async def on_event_past_cancel(
    callback: CallbackQuery, state: FSMContext, lang: str = "en",
) -> None:
    """Пользователь отменил создание события с прошедшей датой."""
    await callback.message.edit_text(t(lang, "cb.confirm.cancelled"))
    await state.clear()
    await callback.answer()
