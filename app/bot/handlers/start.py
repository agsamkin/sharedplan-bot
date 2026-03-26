import logging

from aiogram import Bot, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DEFAULT_REMINDER_SETTINGS, User
from app.services import space_service

logger = logging.getLogger(__name__)
router = Router()


async def _upsert_user(session: AsyncSession, message: Message) -> None:
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


@router.message(CommandStart(deep_link=True))
async def cmd_start_join(
    message: Message, session: AsyncSession, command: CommandObject, bot: Bot
) -> None:
    await _upsert_user(session, message)

    payload = command.args or ""
    if not payload.startswith("join_"):
        # Не join deep link — показываем приветствие
        await _send_welcome(message)
        return

    invite_code = payload[5:]  # убираем "join_"
    space = await space_service.get_space_by_invite_code(session, invite_code)
    if not space:
        await message.answer("Ссылка недействительна или пространство удалено.")
        return

    membership = await space_service.join_space(session, message.from_user.id, space.id)
    if membership is None:
        await message.answer(f"Ты уже состоишь в пространстве «{space.name}».")
        return

    await message.answer(f"Ты присоединился к пространству «{space.name}»!")

    # Уведомляем текущих участников
    members = await space_service.get_space_members(session, space.id)
    joiner_name = message.from_user.first_name
    for member in members:
        if member["user_id"] == message.from_user.id:
            continue
        try:
            await bot.send_message(
                member["user_id"],
                f"👋 {joiner_name} присоединился к «{space.name}»!",
            )
        except Exception:
            logger.warning(
                "Не удалось уведомить пользователя %s о join в space %s",
                member["user_id"],
                space.id,
            )


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    await _upsert_user(session, message)
    await _send_welcome(message)


async def _send_welcome(message: Message) -> None:
    await message.answer(
        "Привет! Я бот для совместного планирования событий.\n\n"
        "Создай пространство командой /newspace, "
        "пригласи участников по ссылке и добавляй события текстом или голосом.\n\n"
        "Введи /help для списка команд."
    )
