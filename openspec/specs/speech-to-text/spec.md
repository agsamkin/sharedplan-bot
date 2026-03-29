# Capability: speech-to-text

## Purpose

Async-клиент Nexara API для транскрипции голосовых сообщений (аудио → текст). Изолированный сервис в `services/speech_to_text.py`.

## Requirements

### Requirement: Async-клиент Nexara API для транскрипции аудио

Модуль `services/speech_to_text.py` ДОЛЖЕН предоставлять async-функцию `transcribe(audio_bytes: bytes) -> str` для транскрипции аудио через Nexara API.

Клиент ДОЛЖЕН:
- Отправлять POST-запрос на `https://api.nexara.ru/api/v1/audio/transcriptions`
- Использовать `Authorization: Bearer {NEXARA_API_KEY}` из конфигурации
- Передавать аудио как `multipart/form-data` с полем `file` (filename `voice.ogg`, content type `audio/ogg`)
- Указывать `response_format: "json"` в форме
- Использовать `aiohttp.ClientSession` для async HTTP

#### Scenario: Успешная транскрипция
- **WHEN** вызывается `transcribe(audio_bytes)` с валидными аудиобайтами
- **THEN** возвращается строка с распознанным текстом из поля `text` JSON-ответа Nexara

#### Scenario: Пустой текст в ответе
- **WHEN** Nexara возвращает `{"text": ""}` или `{"text": "   "}`
- **THEN** выбрасывается `TranscriptionError` с типом `empty_result`

### Requirement: Таймаут и retry при ошибках сервера

Клиент ДОЛЖЕН использовать таймаут 30 секунд на запрос. При HTTP 5xx ДОЛЖЕН выполнять до 2 попыток с экспоненциальным backoff (2 секунды, 4 секунды).

#### Scenario: Таймаут запроса
- **WHEN** Nexara не отвечает в течение 30 секунд
- **THEN** выбрасывается `TranscriptionError` с типом `timeout`

#### Scenario: HTTP 500 с последующим успехом
- **WHEN** первый запрос возвращает HTTP 500, второй — HTTP 200 с текстом
- **THEN** возвращается текст из второго запроса

#### Scenario: Все попытки исчерпаны
- **WHEN** оба запроса возвращают HTTP 5xx
- **THEN** выбрасывается `TranscriptionError` с типом `service_unavailable`

### Requirement: Обработка клиентских ошибок

При HTTP 4xx (кроме 429) клиент НЕ ДОЛЖЕН повторять запрос — это ошибка на стороне клиента.

#### Scenario: HTTP 401 Unauthorized
- **WHEN** Nexara возвращает HTTP 401
- **THEN** выбрасывается `TranscriptionError` с типом `auth_error`

#### Scenario: HTTP 400 Bad Request
- **WHEN** Nexara возвращает HTTP 400
- **THEN** выбрасывается `TranscriptionError` с типом `bad_request`

### Requirement: Логирование вызовов

Каждый вызов `transcribe()` ДОЛЖЕН логировать: длительность запроса (ms), размер аудио (bytes), длину транскрипции (символы). При ошибках ДОЛЖЕН логировать HTTP-статус и тело ответа.

#### Scenario: Успешный вызов
- **WHEN** транскрипция завершилась успешно
- **THEN** в лог записывается: `duration_ms`, `audio_size_bytes`, `transcription_length`

#### Scenario: Ошибочный вызов
- **WHEN** транскрипция завершилась ошибкой
- **THEN** в лог записывается: `duration_ms`, `audio_size_bytes`, `http_status`, `error_body`

### Requirement: Проверка доступности сервиса STT

Функция `transcribe()` ДОЛЖНА проверять наличие `NEXARA_API_KEY` в конфигурации перед выполнением запроса. При отсутствии ключа ДОЛЖНА выбрасывать `TranscriptionError` с типом `service_disabled`.

#### Scenario: NEXARA_API_KEY отсутствует

- **WHEN** вызывается `transcribe(audio_bytes)` и `settings.NEXARA_API_KEY` равен `None`
- **THEN** выбрасывается `TranscriptionError` с `error_type="service_disabled"` без выполнения HTTP-запроса

#### Scenario: NEXARA_API_KEY присутствует

- **WHEN** вызывается `transcribe(audio_bytes)` и `settings.NEXARA_API_KEY` задан
- **THEN** выполняется стандартный запрос к Nexara API

### Requirement: Класс исключения TranscriptionError

Модуль ДОЛЖЕН определять класс `TranscriptionError(Exception)` с атрибутом `error_type: str` для типизированной обработки ошибок в хендлере.

Возможные значения `error_type`: `timeout`, `service_unavailable`, `auth_error`, `bad_request`, `empty_result`, `service_disabled`.

#### Scenario: TranscriptionError содержит тип ошибки
- **WHEN** возникает ошибка транскрипции
- **THEN** `TranscriptionError` содержит `error_type` с одним из определённых значений и текстовое описание ошибки
