from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DEFAULT_REMINDER_SETTINGS, User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    stmt = pg_insert(User).values(
        id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        reminder_settings=DEFAULT_REMINDER_SETTINGS,
    ).on_conflict_do_update(
        index_elements=[User.id],
        set_={
            "first_name": message.from_user.first_name,
            "username": message.from_user.username,
        },
    )
    await session.execute(stmt)

    await message.answer(
        "Привет! Я бот для совместного планирования событий.\n\n"
        "Создай пространство командой /newspace, "
        "пригласи участников по ссылке и добавляй события текстом или голосом.\n\n"
        "Введи /help для списка команд."
    )
