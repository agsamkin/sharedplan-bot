import logging
from datetime import date, datetime

from aiogram import Bot, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.not_command import NotCommandFilter
from app.bot.formatting import (
    PARSE_ERROR_MESSAGES,
    format_confirmation,
    format_conflict_warning,
    format_date_with_weekday,
)
from app.bot.keyboards.confirm import event_confirm_keyboard, event_past_date_keyboard
from app.bot.keyboards.space_select import space_select_keyboard
from app.bot.states.create_event import CreateEvent
from app.services import event_service, space_service
from app.config import settings
from app.services.llm_parser import ParseError, ParsedEvent, parse_event

logger = logging.getLogger(__name__)
router = Router()


def _is_event_in_past(event_date: date, event_time=None) -> bool:
    """Проверить, прошло ли событие: учитывает и дату, и время."""
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(settings.TIMEZONE)
    now = datetime.now(tz)
    if event_date < now.date():
        return True
    if event_date == now.date() and event_time is not None:
        return event_time < now.time()
    return False


async def _show_confirmation_or_past_warning(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    space_id: str,
    parsed: ParsedEvent,
    transcript: str | None = None,
) -> None:
    """Показать карточку подтверждения или предупреждение о прошедшей дате."""
    if _is_event_in_past(parsed.event_date, parsed.event_time):
        await state.set_state(CreateEvent.waiting_for_past_confirm)
        await message.answer(
            f"⚠️ Дата уже прошла ({format_date_with_weekday(parsed.event_date)}).\n\n"
            f"📝 {parsed.title}\n\n"
            "Всё равно создать?",
            reply_markup=event_past_date_keyboard(),
        )
    else:
        from uuid import UUID
        conflict_warning = None
        if parsed.event_time is not None:
            conflicts = await event_service.find_conflicting_events(
                session, UUID(space_id), parsed.event_date, parsed.event_time,
            )
            if conflicts:
                conflict_warning = format_conflict_warning(conflicts)

        await state.set_state(CreateEvent.waiting_for_confirm)
        await message.answer(
            format_confirmation(
                parsed.title, parsed.event_date, parsed.event_time,
                transcript=transcript, conflict_warning=conflict_warning,
            ),
            reply_markup=event_confirm_keyboard(),
        )


async def process_parsed_event(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
    parsed: ParsedEvent,
    raw_input: str,
    transcript: str | None = None,
) -> None:
    """Общая логика после парсинга: выбор пространства, FSM, карточка подтверждения."""
    spaces = await space_service.get_user_spaces(session, message.from_user.id)

    if not spaces:
        await message.answer(
            "У тебя пока нет пространств. Создай первое через /newspace!"
        )
        return

    await state.update_data(
        parsed_title=parsed.title,
        parsed_date=parsed.event_date.isoformat(),
        parsed_time=parsed.event_time.strftime("%H:%M") if parsed.event_time else None,
        raw_input=raw_input,
        transcript=transcript,
    )

    if len(spaces) == 1:
        space_id = str(spaces[0]["id"])
        await state.update_data(space_id=space_id)
        await _show_confirmation_or_past_warning(
            message, state, session, space_id, parsed, transcript,
        )
    else:
        await state.set_state(CreateEvent.waiting_for_space)
        await message.answer(
            "В какое пространство добавить событие?",
            reply_markup=space_select_keyboard(spaces, "event"),
        )


MAX_EVENT_TEXT_LENGTH = 1000


@router.message(StateFilter(None), NotCommandFilter())
async def handle_text_event(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
) -> None:
    """Перехват текстовых сообщений (не команд) для создания событий."""
    text = (message.text or "").strip()
    if not text:
        return

    if len(text) > MAX_EVENT_TEXT_LENGTH:
        await message.answer(
            f"❌ Слишком длинное сообщение. Опиши событие короче (до {MAX_EVENT_TEXT_LENGTH} символов)."
        )
        return

    logger.info("event_create user_id=%d", message.from_user.id)
    await bot.send_chat_action(message.chat.id, "typing")

    try:
        parsed = await parse_event(text)
    except ParseError as e:
        await message.answer(f"❌ {PARSE_ERROR_MESSAGES.get(e.error_type, str(e))}")
        return

    await process_parsed_event(message, state, session, bot, parsed, raw_input=text)
