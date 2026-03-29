import logging

from aiogram import Bot, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import DEFAULT_REMINDER_SETTINGS, User
from app.i18n import normalize_language, t
from app.services import space_service

logger = logging.getLogger(__name__)
router = Router()


async def _upsert_user(session: AsyncSession, message: Message) -> None:
    detected_lang = normalize_language(message.from_user.language_code)
    stmt = pg_insert(User).values(
        id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        reminder_settings=DEFAULT_REMINDER_SETTINGS,
        language=detected_lang,
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
    message: Message, session: AsyncSession, command: CommandObject, bot: Bot,
    lang: str = "en",
) -> None:
    logger.info("/start user_id=%d deep_link=%s", message.from_user.id, command.args)
    await _upsert_user(session, message)

    payload = command.args or ""
    if not payload.startswith("join_"):
        # Не join deep link — показываем приветствие
        await _send_welcome(message, session, lang)
        return

    invite_code = payload[5:]  # убираем "join_"
    space = await space_service.get_space_by_invite_code(session, invite_code)
    if not space:
        await message.answer(t(lang, "start.join.invalid_link"))
        return

    membership = await space_service.join_space(session, message.from_user.id, space.id)
    if membership is None:
        await message.answer(t(lang, "start.join.already_member", name=space.name))
        return

    await message.answer(t(lang, "start.join.success", name=space.name))

    # Уведомляем текущих участников
    members = await space_service.get_space_members(session, space.id)
    joiner_name = message.from_user.first_name
    for member in members:
        if member["user_id"] == message.from_user.id:
            continue
        try:
            await bot.send_message(
                member["user_id"],
                t(lang, "start.join.notification", joiner=joiner_name, space=space.name),
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
async def cmd_start(message: Message, session: AsyncSession, lang: str = "en") -> None:
    logger.info("/start user_id=%d", message.from_user.id)
    await _upsert_user(session, message)
    await _send_welcome(message, session, lang)


def _webapp_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Inline-кнопка для открытия Mini App."""
    url = settings.MINI_APP_URL
    if not url:
        return InlineKeyboardMarkup(inline_keyboard=[])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "start.open_app"), web_app=WebAppInfo(url=url))]
    ])


async def _send_welcome(message: Message, session: AsyncSession, lang: str = "en") -> None:
    spaces = await space_service.get_user_spaces(session, message.from_user.id)

    intro = t(lang, "start.welcome.intro")

    if spaces:
        names = ", ".join(f"\u00ab{s['name']}\u00bb" for s in spaces)
        intro += t(lang, "start.welcome.spaces", names=names)
        intro += t(lang, "start.welcome.has_spaces")
    else:
        intro += t(lang, "start.welcome.no_spaces")

    await message.answer(intro, reply_markup=_webapp_keyboard(lang))
