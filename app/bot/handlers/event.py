import logging

from aiogram import Bot, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.not_command import NotCommandFilter
from app.bot.formatting import PARSE_ERROR_MESSAGES, format_confirmation
from app.bot.keyboards.confirm import event_confirm_keyboard
from app.bot.keyboards.space_select import space_select_keyboard
from app.bot.states.create_event import CreateEvent
from app.services import space_service
from app.services.llm_parser import ParseError, ParsedEvent, parse_event

logger = logging.getLogger(__name__)
router = Router()


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
            "Ты пока не состоишь ни в одном пространстве.\n"
            "Создай новое через /newspace"
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
        await state.update_data(space_id=str(spaces[0]["id"]))
        await state.set_state(CreateEvent.waiting_for_confirm)
        await message.answer(
            format_confirmation(
                parsed.title, parsed.event_date, parsed.event_time, transcript=transcript,
            ),
            reply_markup=event_confirm_keyboard(),
        )
    else:
        await state.set_state(CreateEvent.waiting_for_space)
        await message.answer(
            "В какое пространство добавить событие?",
            reply_markup=space_select_keyboard(spaces, "event"),
        )


@router.message(StateFilter(None), NotCommandFilter())
async def handle_text_event(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
) -> None:
    """Перехват текстовых сообщений (не команд) для создания событий."""
    await bot.send_chat_action(message.chat.id, "typing")

    try:
        parsed = await parse_event(message.text)
    except ParseError as e:
        await message.answer(f"❌ {PARSE_ERROR_MESSAGES.get(e.error_type, str(e))}")
        return

    await process_parsed_event(message, state, session, bot, parsed, raw_input=message.text)
