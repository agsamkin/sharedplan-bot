import logging
from io import BytesIO

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.formatting import get_parse_error_message, get_stt_error_message
from app.bot.handlers.event import MAX_EVENT_TEXT_LENGTH, process_parsed_event
from app.config import settings
from app.i18n import t
from app.services.llm_parser import ParseError, parse_event
from app.services.speech_to_text import TranscriptionError, transcribe

logger = logging.getLogger(__name__)
router = Router()

MAX_VOICE_DURATION_SECONDS = 120  # 2 минуты
MAX_VOICE_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 МБ


@router.message(StateFilter(None), F.voice)
async def handle_voice_event(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
    lang: str = "en",
) -> None:
    """Перехват голосовых сообщений для создания событий."""
    voice = message.voice

    if voice.duration > MAX_VOICE_DURATION_SECONDS:
        await message.answer(
            t(lang, "voice.too_long",
              duration=voice.duration,
              max_duration=MAX_VOICE_DURATION_SECONDS)
        )
        return

    if voice.file_size and voice.file_size > MAX_VOICE_FILE_SIZE_BYTES:
        await message.answer(t(lang, "voice.too_large"))
        return

    await bot.send_chat_action(message.chat.id, "typing")

    # Скачивание аудио в память
    file = await bot.get_file(voice.file_id)
    buffer = BytesIO()
    await bot.download_file(file.file_path, buffer)
    audio_bytes = buffer.getvalue()

    # Транскрипция
    try:
        transcript = await transcribe(audio_bytes)
    except TranscriptionError as e:
        log = logger.error if e.error_type == "auth_error" else logger.warning
        log("STT error: type=%s message=%s", e.error_type, e)
        await message.answer(f"\u274c {get_stt_error_message(lang, e.error_type)}")
        return

    if len(transcript) > MAX_EVENT_TEXT_LENGTH:
        await message.answer(
            t(lang, "voice.transcript_too_long",
              transcript=transcript[:200],
              max_len=MAX_EVENT_TEXT_LENGTH)
        )
        return

    logger.info("event_create_voice user_id=%d", message.from_user.id)

    # LLM-парсинг транскрипции
    try:
        parsed = await parse_event(transcript)
    except ParseError as e:
        error_text = (
            f"\ud83c\udfa4 {transcript}\n\n"
            f"\u274c {get_parse_error_message(lang, e.error_type)}"
        )
        reply_markup = None
        if e.error_type == "service_disabled" and settings.MINI_APP_URL:
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=t(lang, "event.open_app"),
                    web_app=WebAppInfo(url=settings.MINI_APP_URL),
                ),
            ]])
        await message.answer(error_text, reply_markup=reply_markup)
        return

    await process_parsed_event(
        message, state, session, bot, parsed, raw_input=transcript, transcript=transcript,
        lang=lang,
    )
