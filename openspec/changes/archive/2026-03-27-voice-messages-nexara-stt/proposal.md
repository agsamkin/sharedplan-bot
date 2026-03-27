## Why

Бот поддерживает создание событий только из текста. Пользователям удобнее отправить голосовое сообщение, чем набирать текст — особенно на мобильном устройстве. Фаза 5 добавляет voice-to-event пайплайн: голосовое сообщение → транскрипция через Nexara API → парсинг через LLM → подтверждение с отображением транскрипции.

## What Changes

- Новый сервис `speech_to_text.py` — async-клиент Nexara API для транскрипции аудио (OGG/Opus → текст)
- Новый обработчик `voice.py` — перехват голосовых сообщений Telegram, скачивание аудио в память, отправка на транскрипцию, передача текста в существующий event flow
- Карточка подтверждения дополняется строкой с транскрипцией (`🎤 Распознано: «...»`), чтобы пользователь видел, что было распознано
- Сохранение транскрипции в `events.raw_input` для отладки

## Capabilities

### New Capabilities
- `speech-to-text`: Async-клиент Nexara API — метод `transcribe(audio_bytes)` → `str`, multipart upload через aiohttp, обработка ошибок, retry, логирование
- `voice-event-handler`: Telegram-обработчик голосовых сообщений — скачивание аудио, вызов STT, интеграция с event creation flow, карточка подтверждения с транскрипцией

### Modified Capabilities
- `event-creation`: Добавляется поддержка источника `voice` — карточка подтверждения показывает транскрипцию, `raw_input` сохраняет транскрибированный текст с пометкой источника

## Impact

- **Новые файлы**: `app/services/speech_to_text.py`, `app/bot/handlers/voice.py`
- **Изменяемые файлы**: `app/bot/handlers/event.py` (рефакторинг общей логики для переиспользования из voice handler), `app/bot/keyboards/confirm.py` (карточка с транскрипцией)
- **Зависимости**: `aiohttp` (уже в requirements.txt)
- **Конфигурация**: `NEXARA_API_KEY` (уже в config.py)
- **Внешний API**: Nexara `POST https://api.nexara.ru/api/v1/audio/transcriptions`
