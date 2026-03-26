import logging

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.not_command import NotCommandFilter
from app.bot.formatting import FORMAT_HINT, format_confirmation
from app.bot.keyboards.confirm import event_confirm_keyboard
from app.bot.keyboards.space_select import space_select_keyboard
from app.bot.states.create_event import CreateEvent
from app.services import space_service
from app.services.event_service import parse_event_text

logger = logging.getLogger(__name__)
router = Router()


@router.message(StateFilter(None), NotCommandFilter())
async def handle_text_event(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Перехват текстовых сообщений (не команд) для создания событий."""
    try:
        parsed = await parse_event_text(message.text)
    except ValueError as e:
        await message.answer(f"❌ {e}\n\n{FORMAT_HINT}")
        return

    spaces = await space_service.get_user_spaces(session, message.from_user.id)

    if not spaces:
        await message.answer(
            "Ты пока не состоишь ни в одном пространстве.\n"
            "Создай новое через /newspace"
        )
        return

    await state.update_data(
        parsed_title=parsed.title,
        parsed_date=parsed.date.isoformat(),
        parsed_time=parsed.time.strftime("%H:%M") if parsed.time else None,
        raw_input=message.text,
    )

    if len(spaces) == 1:
        await state.update_data(space_id=str(spaces[0]["id"]))
        await state.set_state(CreateEvent.waiting_for_confirm)
        await message.answer(
            format_confirmation(parsed.title, parsed.date, parsed.time),
            reply_markup=event_confirm_keyboard(),
        )
    else:
        await state.set_state(CreateEvent.waiting_for_space)
        await message.answer(
            "В какое пространство добавить событие?",
            reply_markup=space_select_keyboard(spaces, "event"),
        )
