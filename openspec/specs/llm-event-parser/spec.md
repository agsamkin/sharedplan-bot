# Capability: llm-event-parser

## Purpose

LLM-клиент для парсинга текстовых описаний событий в структурированные данные через OpenRouter API.

## Requirements

### Requirement: LLM-клиент OpenRouter для парсинга событий

Модуль `services/llm_parser.py` ДОЛЖЕН предоставлять функцию `parse_event(user_text: str)`, которая отправляет текст в OpenRouter API и возвращает структурированное событие `ParsedEvent(title: str, event_date: date, event_time: Optional[time])`. Поля `event_date` и `event_time` используют Pydantic `Field(alias="date")` / `Field(alias="time")` для парсинга JSON-ответа LLM с ключами `"date"` и `"time"`.

Клиент ДОЛЖЕН использовать `openai.AsyncOpenAI` с `base_url="https://openrouter.ai/api/v1"` и моделью из `settings.OPENROUTER_MODEL`. Инициализация клиента — ленивая (при первом вызове), а не при импорте модуля.

#### Scenario: Успешный парсинг текста с датой и временем
- **WHEN** вызван `parse_event("Ужин с родителями завтра в 19:00")` при текущей дате 2026-03-27
- **THEN** возвращается `ParsedEvent(title="Ужин с родителями", event_date=2026-03-28, event_time=19:00)`

#### Scenario: Парсинг текста без времени
- **WHEN** вызван `parse_event("День рождения Ани 5 апреля")`
- **THEN** возвращается `ParsedEvent(title="День рождения Ани", event_date=2026-04-05, event_time=None)`

#### Scenario: Относительная дата с днём недели
- **WHEN** вызван `parse_event("Тренировка в понедельник в 8 утра")` при текущей дате пятница 2026-03-27
- **THEN** возвращается `ParsedEvent` с `event_date` = ближайший понедельник (2026-03-30), `event_time=08:00`

### Requirement: Системный промпт с контекстом даты

Модуль `prompts/event_parser.py` ДОЛЖЕН предоставлять функцию `build_messages(user_text, current_date, weekday)`, формирующую список сообщений для LLM API.

Системный промпт ДОЛЖЕН включать: текущую дату, день недели, часовой пояс `Europe/Moscow`, описание ожидаемого JSON-формата `{"title": "...", "date": "YYYY-MM-DD", "time": "HH:MM" | null}`, инструкцию возвращать `time: null` если время не указано.

#### Scenario: Формирование сообщений с текущим контекстом
- **WHEN** вызван `build_messages("Встреча завтра", date(2026, 3, 27), "пятница")`
- **THEN** возвращается список из system message (с датой 2026-03-27, днём «пятница», часовым поясом Europe/Moscow) и user message с текстом пользователя

### Requirement: Валидация ответа LLM через Pydantic

Ответ LLM ДОЛЖЕН валидироваться через Pydantic-модель `ParsedEvent`. При невалидном JSON или отсутствующих/некорректных полях ДОЛЖНО выбрасываться исключение `ParseError`.

#### Scenario: Валидный JSON от LLM
- **WHEN** LLM возвращает `{"title": "Ужин", "date": "2026-03-28", "time": "19:00"}`
- **THEN** создаётся `ParsedEvent` с `title="Ужин"`, `event_date=date(2026,3,28)`, `event_time=time(19,0)`

#### Scenario: JSON с time=null
- **WHEN** LLM возвращает `{"title": "День рождения", "date": "2026-04-05", "time": null}`
- **THEN** создаётся `ParsedEvent` с `event_time=None`

#### Scenario: Невалидный JSON от LLM
- **WHEN** LLM возвращает текст, не являющийся валидным JSON
- **THEN** выбрасывается `ParseError` с типом `invalid_json`

#### Scenario: Отсутствующее обязательное поле
- **WHEN** LLM возвращает `{"title": "Ужин"}` (без поля `date`)
- **THEN** выбрасывается `ParseError` с типом `invalid_json`

### Requirement: Retry при HTTP-ошибках

При получении HTTP 429 (rate limit) или 5xx от OpenRouter клиент ДОЛЖЕН выполнять до 3 повторных попыток с экспоненциальным backoff (1s, 2s, 4s).

#### Scenario: Rate limit с успешным retry
- **WHEN** первый запрос возвращает HTTP 429, второй — успешный ответ
- **THEN** `parse_event` возвращает результат после второй попытки

#### Scenario: Все попытки исчерпаны
- **WHEN** все 3 попытки возвращают HTTP 429
- **THEN** выбрасывается `ParseError` с типом `rate_limit`

#### Scenario: Серверная ошибка 5xx
- **WHEN** OpenRouter возвращает HTTP 500
- **THEN** выполняется retry с backoff, при исчерпании попыток — `ParseError` с типом `network`

### Requirement: Повторная попытка при невалидном JSON

При получении невалидного JSON от LLM клиент ДОЛЖЕН выполнить одну повторную попытку с усиленной инструкцией в промпте.

#### Scenario: Невалидный JSON, успешный retry
- **WHEN** первый ответ LLM не является валидным JSON, повторный запрос возвращает валидный JSON
- **THEN** `parse_event` возвращает результат после повторной попытки

#### Scenario: Повторный невалидный JSON
- **WHEN** оба ответа LLM невалидны
- **THEN** выбрасывается `ParseError` с типом `invalid_json`

### Requirement: Таймаут запроса

Каждый запрос к OpenRouter ДОЛЖЕН иметь таймаут 15 секунд.

#### Scenario: Таймаут превышен
- **WHEN** OpenRouter не отвечает в течение 15 секунд
- **THEN** выбрасывается `ParseError` с типом `timeout`

### Requirement: Параметры LLM-запроса

Запросы к OpenRouter ДОЛЖНЫ использовать `temperature: 0.1` и `response_format: {"type": "json_object"}`.

#### Scenario: Параметры запроса
- **WHEN** выполняется запрос к OpenRouter
- **THEN** запрос содержит `temperature=0.1` и `response_format={"type": "json_object"}`

### Requirement: Логирование LLM-вызовов

Каждый вызов OpenRouter ДОЛЖЕН логироваться с информацией: модель, input_tokens, output_tokens, duration_ms.

#### Scenario: Успешный вызов
- **WHEN** LLM-запрос выполнен успешно
- **THEN** в лог записывается: model, input_tokens, output_tokens, duration_ms

#### Scenario: Неуспешный вызов
- **WHEN** LLM-запрос завершился ошибкой
- **THEN** в лог записывается: model, error_type, duration_ms
