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
    logger.info("/start user_id=%d deep_link=%s", message.from_user.id, command.args)
    await _upsert_user(session, message)

    payload = command.args or ""
    if not payload.startswith("join_"):
        # Не join deep link — показываем приветствие
        await _send_welcome(message, session)
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
        except Exception as e:
            logger.warning(
                "Не удалось уведомить: user_id=%s space_id=%s error_type=%s error=%s",
                member["user_id"],
                space.id,
                type(e).__name__,
                e,
            )


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    logger.info("/start user_id=%d", message.from_user.id)
    await _upsert_user(session, message)
    await _send_welcome(message, session)


async def _send_welcome(message: Message, session: AsyncSession) -> None:
    spaces = await space_service.get_user_spaces(session, message.from_user.id)

    intro = (
        "Привет! Я помогу организовать совместные планы.\n\n"
        "Что я умею:\n"
        "📅 Создавать события из текста или голосовых сообщений\n"
        "👥 Объединять участников в пространства с общим календарём\n"
        "🔔 Отправлять персональные напоминания\n"
    )

    if spaces:
        names = ", ".join(f"«{s['name']}»" for s in spaces)
        intro += f"\nТвои пространства: {names}\n"
        intro += "\nОтправь текст или голосовое, чтобы создать событие.\n"
    else:
        intro += "\nНачни с создания пространства — /newspace\n"

    intro += "Полный список команд — /help"
    await message.answer(intro)
