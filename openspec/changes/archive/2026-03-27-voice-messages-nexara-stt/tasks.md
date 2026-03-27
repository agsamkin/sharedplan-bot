## 1. Сервис транскрипции (speech_to_text.py)

- [x] 1.1 Создать `app/services/speech_to_text.py` с классом `TranscriptionError(Exception)` и атрибутом `error_type`
- [x] 1.2 Реализовать функцию `transcribe(audio_bytes: bytes) -> str` — async POST на Nexara API через aiohttp с multipart upload (file=voice.ogg, response_format=json)
- [x] 1.3 Добавить таймаут 30 секунд, retry до 2 попыток с backoff (2s, 4s) при HTTP 5xx
- [x] 1.4 Добавить обработку ошибок: HTTP 4xx → без retry, пустой текст → `empty_result`, таймаут → `timeout`
- [x] 1.5 Добавить логирование: duration_ms, audio_size_bytes, transcription_length (успех) или http_status, error_body (ошибка)

## 2. Рефакторинг event handler для переиспользования

- [x] 2.1 Извлечь из `event.py` общую функцию `process_parsed_event(message, state, session, bot, parsed, raw_input, transcript=None)` — логика выбора пространства, сохранение в FSM, отображение карточки
- [x] 2.2 Обновить `handle_text_event` для вызова `process_parsed_event` (без transcript)

## 3. Карточка подтверждения с транскрипцией

- [x] 3.1 Обновить `format_confirmation()` в `app/bot/formatting.py` — принимать опциональный параметр `transcript`, добавлять строку `🎤 Распознано: «{transcript}»` перед данными события
- [x] 3.2 Обновить вызовы `format_confirmation()` в event flow — передавать `transcript` из FSM-данных при наличии

## 4. Обработчик голосовых сообщений (voice.py)

- [x] 4.1 Создать `app/bot/handlers/voice.py` с роутером и обработчиком `Message.voice`
- [x] 4.2 Реализовать скачивание аудио через `bot.download(file)` в `BytesIO`
- [x] 4.3 Вызвать `transcribe()` → `parse_event()` → `process_parsed_event()` с передачей transcript
- [x] 4.4 Добавить обработку ошибок STT: сообщения пользователю по типу TranscriptionError
- [x] 4.5 Добавить `chat_action: typing` перед началом обработки

## 5. Регистрация и интеграция

- [x] 5.1 Зарегистрировать `voice.router` в `main.py` (или в месте регистрации роутеров)
- [x] 5.2 Добавить сообщения об ошибках STT в `PARSE_ERROR_MESSAGES` или отдельный словарь в `formatting.py`
- [x] 5.3 Проверить, что голосовые и текстовые сообщения маршрутизируются к правильным обработчикам без конфликтов
