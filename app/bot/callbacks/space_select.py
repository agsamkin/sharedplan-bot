import logging
from datetime import date, time
from uuid import UUID

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.formatting import format_confirmation, format_conflict_warning, format_date_with_weekday
from app.bot.keyboards.confirm import (
    event_confirm_keyboard,
    event_past_date_keyboard,
)
from app.bot.states.create_event import CreateEvent
from app.services import event_service, space_service

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("space_select:"))
async def on_space_select(
    callback: CallbackQuery, session: AsyncSession, bot_username: str, state: FSMContext,
) -> None:
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Неизвестное действие")
        return

    space_id = UUID(parts[1])
    action = parts[2]

    if action == "event":
        data = await state.get_data()
        event_date = date.fromisoformat(data["parsed_date"])
        event_time = time.fromisoformat(data["parsed_time"]) if data.get("parsed_time") else None
        transcript = data.get("transcript")
        await state.update_data(space_id=str(space_id))

        from app.bot.handlers.event import _is_event_in_past
        if _is_event_in_past(event_date, event_time):
            await state.set_state(CreateEvent.waiting_for_past_confirm)
            await callback.message.edit_text(
                f"⚠️ Дата уже прошла ({format_date_with_weekday(event_date)}).\n\n"
                f"📝 {data['parsed_title']}\n\n"
                "Всё равно создать?",
                reply_markup=event_past_date_keyboard(),
            )
        else:
            conflict_warning = None
            if event_time is not None:
                conflicts = await event_service.find_conflicting_events(
                    session, space_id, event_date, event_time,
                )
                if conflicts:
                    conflict_warning = format_conflict_warning(conflicts)

            await state.set_state(CreateEvent.waiting_for_confirm)
            await callback.message.edit_text(
                format_confirmation(
                    data["parsed_title"], event_date, event_time,
                    transcript=transcript, conflict_warning=conflict_warning,
                ),
                reply_markup=event_confirm_keyboard(),
            )

    else:
        await callback.answer("Это действие доступно в приложении")

    await callback.answer()
