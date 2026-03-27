import logging
from io import BytesIO

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.formatting import PARSE_ERROR_MESSAGES, STT_ERROR_MESSAGES
from app.bot.handlers.event import process_parsed_event
from app.services.llm_parser import ParseError, parse_event
from app.services.speech_to_text import TranscriptionError, transcribe

logger = logging.getLogger(__name__)
router = Router()


@router.message(StateFilter(None), F.voice)
async def handle_voice_event(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
) -> None:
    """Перехват голосовых сообщений для создания событий."""
    await bot.send_chat_action(message.chat.id, "typing")

    # Скачивание аудио в память
    file = await bot.get_file(message.voice.file_id)
    buffer = BytesIO()
    await bot.download_file(file.file_path, buffer)
    audio_bytes = buffer.getvalue()

    # Транскрипция
    try:
        transcript = await transcribe(audio_bytes)
    except TranscriptionError as e:
        log = logger.error if e.error_type == "auth_error" else logger.warning
        log("STT error: type=%s message=%s", e.error_type, e)
        await message.answer(f"❌ {STT_ERROR_MESSAGES.get(e.error_type, str(e))}")
        return

    # LLM-парсинг транскрипции
    try:
        parsed = await parse_event(transcript)
    except ParseError as e:
        await message.answer(
            f"🎤 Распознано: «{transcript}»\n\n"
            f"❌ {PARSE_ERROR_MESSAGES.get(e.error_type, str(e))}"
        )
        return

    await process_parsed_event(
        message, state, session, bot, parsed, raw_input=transcript, transcript=transcript,
    )
