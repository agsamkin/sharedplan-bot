import logging

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.states.create_space import CreateSpace
from app.config import settings
from app.services import space_service

logger = logging.getLogger(__name__)
router = Router()


# --- /newspace ---


@router.message(Command("newspace"))
async def cmd_newspace(message: Message, state: FSMContext) -> None:
    logger.info("/newspace user_id=%d", message.from_user.id)
    await state.set_state(CreateSpace.waiting_for_name)
    await message.answer("Как назовём пространство?")


@router.message(CreateSpace.waiting_for_name)
async def process_space_name(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не может быть пустым. Введи название пространства:")
        return
    if len(name) > 255:
        await message.answer("Слишком длинное название. Попробуй покороче (до 255 символов).")
        return

    space = await space_service.create_space(session, message.from_user.id, name)
    await state.clear()

    bot_info = await bot.get_me()
    invite_link = f"https://t.me/{bot_info.username}?start=join_{space.invite_code}"

    await message.answer(
        f"✅ Пространство «{space.name}» создано!\n\n"
        f"🔗 Ссылка для приглашения:\n{invite_link}\n\n"
        "Отправь эту ссылку тем, кого хочешь добавить."
    )


# --- /spaces ---


@router.message(Command("spaces"))
async def cmd_spaces(message: Message, session: AsyncSession) -> None:
    logger.info("/spaces user_id=%d", message.from_user.id)
    spaces = await space_service.get_user_spaces(session, message.from_user.id)
    if not spaces:
        await message.answer(
            "У тебя пока нет пространств. Создай первое через /newspace!"
        )
        return

    lines = ["📂 Твои про��транства:\n"]
    for i, s in enumerate(spaces, 1):
        role_icon = "👑" if s["role"] == "admin" else "👤"
        count = s["member_count"]
        lines.append(f"{i}. {role_icon} {s['name']} ({count} уч.)")

    buttons = []
    if settings.MINI_APP_URL:
        buttons.append([InlineKeyboardButton(
            text="📂 Управление пространствами",
            web_app=WebAppInfo(url=settings.MINI_APP_URL),
        )])

    await message.answer(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None,
    )


# --- /space_info ---


@router.message(Command("space_info"))
async def cmd_space_info(message: Message) -> None:
    logger.info("/space_info user_id=%d", message.from_user.id)
    if settings.MINI_APP_URL:
        await message.answer(
            "Открой приложение для просмотра информации о пространствах:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="ℹ️ Информация о пространстве",
                    web_app=WebAppInfo(url=settings.MINI_APP_URL),
                )]
            ]),
        )
    else:
        await message.answer("Mini App пока не настроен.")
