import logging
from uuid import UUID

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.formatting import format_date_relative
from app.bot.keyboards.space_select import space_select_keyboard
from app.services import event_service, space_service

logger = logging.getLogger(__name__)
router = Router()


async def _send_events_list(
    message: Message, session: AsyncSession, space_id: UUID,
    edit: bool = False, user_id: int | None = None,
) -> None:
    """Отправить список событий пространства."""
    space = await space_service.get_space_by_id(session, space_id)
    if not space:
        text = "Пространство не найдено."
        if edit:
            await message.edit_text(text)
        else:
            await message.answer(text)
        return

    events = await event_service.get_upcoming_events(session, space_id)
    if not events:
        text = f"📅 Нет предстоящих событий в «{space.name}»."
        if edit:
            await message.edit_text(text)
        else:
            await message.answer(text)
        return

    lines = [f"📅 Ближайшие события в «{space.name}»:\n"]
    for i, ev in enumerate(events, 1):
        date_str = format_date_relative(ev.event_date)
        if ev.event_time is not None:
            lines.append(f"{i}. {ev.title} — {date_str}, {ev.event_time.strftime('%H:%M')}")
        else:
            lines.append(f"{i}. {ev.title} — {date_str}")

    text = "\n".join(lines)

    # Inline-кнопки управления для событий текущего пользователя
    buttons = []
    if user_id is not None:
        for ev in events:
            if ev.created_by == user_id:
                buttons.append([
                    InlineKeyboardButton(
                        text=f"⚙️ {ev.title}",
                        callback_data=f"event_manage:{ev.id}",
                    )
                ])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None

    if edit:
        await message.edit_text(text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)


@router.message(Command("events"))
async def cmd_events(message: Message, session: AsyncSession) -> None:
    logger.info("/events user_id=%d", message.from_user.id)
    spaces = await space_service.get_user_spaces(session, message.from_user.id)

    if not spaces:
        await message.answer(
            "У тебя пока нет пространств. Создай первое через /newspace!"
        )
        return

    if len(spaces) == 1:
        await _send_events_list(message, session, spaces[0]["id"], user_id=message.from_user.id)
    else:
        await message.answer(
            "Выбери пространство:",
            reply_markup=space_select_keyboard(spaces, "events"),
        )
