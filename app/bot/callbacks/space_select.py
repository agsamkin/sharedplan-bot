import logging
from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.confirm import delete_space_confirm_keyboard
from app.services import space_service

logger = logging.getLogger(__name__)
router = Router()


def format_space_info(space_name: str, members: list[dict], invite_link: str) -> str:
    """Форматирование информации о пространстве. Используется из handlers и callbacks."""
    lines = [f"📋 Пространство: {space_name}\n"]
    lines.append("👥 Участники:")
    for m in members:
        role_badge = "👑" if m["role"] == "admin" else "👤"
        name = m["first_name"]
        if m["username"]:
            name += f" (@{m['username']})"
        lines.append(f"  {role_badge} {name}")
    lines.append(f"\n🔗 Ссылка-приглашение:\n{invite_link}")
    return "\n".join(lines)


@router.callback_query(F.data.startswith("space_select:"))
async def on_space_select(
    callback: CallbackQuery, session: AsyncSession, bot_username: str
) -> None:
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Неизвестное действие")
        return

    space_id = UUID(parts[1])
    action = parts[2]

    if action == "info":
        space = await space_service.get_space_by_id(session, space_id)
        if not space:
            await callback.answer("Пространство не найдено")
            return
        members = await space_service.get_space_members(session, space_id)
        invite_link = f"https://t.me/{bot_username}?start=join_{space.invite_code}"
        text = format_space_info(space.name, members, invite_link)
        await callback.message.edit_text(text)

    elif action == "kick":
        space = await space_service.get_space_by_id(session, space_id)
        if not space:
            await callback.answer("Пространство не найдено")
            return
        is_admin = await space_service.check_admin(session, space_id, callback.from_user.id)
        if not is_admin:
            await callback.message.edit_text("Только администратор может удалять участников.")
            return
        members = await space_service.get_space_members(session, space_id)
        other_members = [m for m in members if m["user_id"] != callback.from_user.id]
        if not other_members:
            await callback.message.edit_text("В пространстве нет других участников.")
            return
        names = "\n".join(
            f"  @{m['username']}" if m["username"] else f"  {m['first_name']} (нет username)"
            for m in other_members
        )
        await callback.message.edit_text(
            f"Отправь команду:\n/kick @username\n\nУчастники «{space.name}»:\n{names}"
        )

    elif action == "delete":
        space = await space_service.get_space_by_id(session, space_id)
        if not space:
            await callback.answer("Пространство не найдено")
            return
        is_admin = await space_service.check_admin(session, space_id, callback.from_user.id)
        if not is_admin:
            await callback.message.edit_text("Только администратор может удалить пространство.")
            return
        await callback.message.edit_text(
            f"Удалить пространство «{space.name}»?\n"
            "Все события и напоминания будут удалены.",
            reply_markup=delete_space_confirm_keyboard(space_id),
        )

    await callback.answer()
