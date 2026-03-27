import logging
from uuid import UUID

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.callbacks.space_select import format_space_info
from app.bot.keyboards.confirm import delete_space_confirm_keyboard
from app.bot.keyboards.space_select import space_select_keyboard
from app.bot.states.create_space import CreateSpace
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

    lines = ["📂 Твои пространства:\n"]
    for i, s in enumerate(spaces, 1):
        role_icon = "👑" if s["role"] == "admin" else "👤"
        count = s["member_count"]
        lines.append(f"{i}. {role_icon} {s['name']} ({count} уч.)")
    await message.answer("\n".join(lines))


# --- /space_info ---


@router.message(Command("space_info"))
async def cmd_space_info(
    message: Message, session: AsyncSession, bot: Bot
) -> None:
    logger.info("/space_info user_id=%d", message.from_user.id)
    spaces = await space_service.get_user_spaces(session, message.from_user.id)
    if not spaces:
        await message.answer("У тебя пока нет пространств. Создай первое через /newspace!")
        return

    if len(spaces) == 1:
        await _send_space_info(message, session, spaces[0]["id"], bot)
    else:
        await message.answer(
            "Выбери пространство:",
            reply_markup=space_select_keyboard(spaces, "info"),
        )


async def _send_space_info(
    message: Message, session: AsyncSession, space_id: UUID, bot: Bot
) -> None:
    space = await space_service.get_space_by_id(session, space_id)
    if not space:
        await message.answer("Пространство не найдено.")
        return

    members = await space_service.get_space_members(session, space_id)
    bot_info = await bot.get_me()
    invite_link = f"https://t.me/{bot_info.username}?start=join_{space.invite_code}"
    await message.answer(format_space_info(space.name, members, invite_link))


# --- /kick ---


@router.message(Command("kick"))
async def cmd_kick(message: Message, session: AsyncSession) -> None:
    logger.info("/kick user_id=%d", message.from_user.id)
    spaces = await space_service.get_user_spaces(session, message.from_user.id)
    admin_spaces = [s for s in spaces if s["role"] == "admin"]

    if not admin_spaces:
        await message.answer("Только администратор может удалять участников.")
        return

    # Парсим username из команды: /kick @username
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи пользователя: /kick @username")
        return

    target_username = parts[1].lstrip("@").strip()
    if not target_username:
        await message.answer("Укажи пользователя: /kick @username")
        return

    if len(admin_spaces) == 1:
        await _do_kick(message, session, admin_spaces[0]["id"], admin_spaces[0]["name"], target_username)
    else:
        # Нужен выбор пространства — но kick требует username,
        # поэтому показываем список и просим повторить для конкретного
        await message.answer(
            "Ты админ в нескольких пространствах. Выбери пространство:",
            reply_markup=space_select_keyboard(admin_spaces, "kick"),
        )


async def _do_kick(
    message: Message,
    session: AsyncSession,
    space_id: UUID,
    space_name: str,
    target_username: str,
) -> None:
    # Проверяем что не пытается кикнуть себя
    if message.from_user.username and target_username.lower() == message.from_user.username.lower():
        await message.answer("Нельзя удалить себя из пространства.")
        return

    member = await space_service.find_member_by_username(session, space_id, target_username)
    if not member:
        await message.answer(f"Пользователь @{target_username} не найден в «{space_name}».")
        return

    if member["role"] == "admin":
        await message.answer("Нельзя удалить администратора пространства.")
        return

    await space_service.kick_member(session, space_id, member["user_id"])
    await message.answer(f"Пользователь @{target_username} удалён из «{space_name}».")


# --- /delete_space ---


@router.message(Command("delete_space"))
async def cmd_delete_space(message: Message, session: AsyncSession) -> None:
    logger.info("/delete_space user_id=%d", message.from_user.id)
    spaces = await space_service.get_user_spaces(session, message.from_user.id)
    admin_spaces = [s for s in spaces if s["role"] == "admin"]

    if not admin_spaces:
        await message.answer("Только администратор может удалить пространство.")
        return

    if len(admin_spaces) == 1:
        space_id = admin_spaces[0]["id"]
        space_name = admin_spaces[0]["name"]
        await message.answer(
            f"Удалить пространство «{space_name}»?\n"
            "Все события и напоминания будут удалены.",
            reply_markup=delete_space_confirm_keyboard(space_id),
        )
    else:
        await message.answer(
            "Выбери пространство для удаления:",
            reply_markup=space_select_keyboard(admin_spaces, "delete"),
        )


@router.callback_query(F.data.startswith("delete_space_confirm:"))
async def on_delete_space_confirm(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    space_id = UUID(callback.data.split(":")[1])

    is_admin = await space_service.check_admin(session, space_id, callback.from_user.id)
    if not is_admin:
        await callback.answer("Нет прав для этого действия.")
        return

    space = await space_service.get_space_by_id(session, space_id)
    space_name = space.name if space else "Неизвестное"

    await space_service.delete_space(session, space_id)
    await callback.message.edit_text(f"Пространство «{space_name}» удалено.")
    await callback.answer()


@router.callback_query(F.data.startswith("delete_space_cancel:"))
async def on_delete_space_cancel(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Удаление отменено.")
    await callback.answer()
