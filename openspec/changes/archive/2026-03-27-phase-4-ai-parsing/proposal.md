## Why

Сейчас создание событий требует структурированного ввода в формате `название, ДД.ММ.ГГГГ, ЧЧ:ММ` — это неудобно и противоречит основной концепции бота, где пользователь пишет в свободной форме («Ужин с родителями завтра в 19:00»). Фаза 4 заменяет заглушку парсинга на AI-извлечение через OpenRouter API, делая бот пригодным к повседневному использованию.

## What Changes

- **Новый сервис `services/llm_parser.py`**: клиент OpenRouter API через `openai` SDK с кастомным `base_url`, метод `parse_event()` для извлечения `{title, date, time}` из произвольного текста
- **Новый модуль `prompts/event_parser.py`**: системный и пользовательский промпты для LLM с контекстом текущей даты, дня недели, часового пояса
- **Замена заглушки парсинга в `bot/handlers/event.py`**: вместо ручного формата — вызов `llm_parser.parse_event()`
- **Обработка ошибок AI-пайплайна**: retry при 429/5xx, таймаут 15 сек, повторная попытка при невалидном JSON, понятные сообщения пользователю
- **Pydantic-модель `ParsedEvent`**: валидация ответа LLM (title: str, date: date, time: Optional[time])

## Capabilities

### New Capabilities
- `llm-event-parser`: AI-парсинг текста в структурированное событие через OpenRouter API — клиент, промпты, валидация, retry-логика

### Modified Capabilities
- `event-creation`: замена заглушки структурированного парсинга (`parse_event_text`) на вызов LLM (`llm_parser.parse_event`); изменение формата ошибок при неудачном парсинге; удаление инструкций о формате `название, ДД.ММ.ГГГГ, ЧЧ:ММ`

## Impact

- **Код**: `services/llm_parser.py` (новый), `prompts/event_parser.py` (новый), `bot/handlers/event.py` (модификация), `bot/callbacks/event_confirm.py` (модификация сообщения при редактировании)
- **Зависимости**: `openai` SDK (уже в requirements.txt)
- **Внешние API**: OpenRouter API — новая runtime-зависимость, требует `OPENROUTER_API_KEY` и `OPENROUTER_MODEL` (уже в конфигурации)
- **Конфигурация**: без изменений — переменные `OPENROUTER_API_KEY` и `OPENROUTER_MODEL` уже определены в `config.py`
