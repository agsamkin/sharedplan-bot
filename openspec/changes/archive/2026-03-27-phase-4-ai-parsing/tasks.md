## 1. Pydantic-модель и исключения

- [x] 1.1 Создать `app/services/llm_parser.py` с Pydantic-моделью `ParsedEvent(title: str, date: date, time: Optional[time])` и исключением `ParseError(type: Literal["invalid_json", "timeout", "network", "rate_limit"], message: str)`
- [x] 1.2 Удалить `dataclass ParsedEvent` и функцию `parse_event_text()` из `app/services/event_service.py`

## 2. Промпты

- [x] 2.1 Создать `app/prompts/__init__.py`
- [x] 2.2 Создать `app/prompts/event_parser.py` с функцией `build_messages(user_text, current_date, weekday)` — системный промпт с текущей датой, днём недели, часовым поясом Europe/Moscow, описанием JSON-формата; user message с текстом пользователя

## 3. LLM-клиент

- [x] 3.1 Реализовать функцию `parse_event(user_text: str)` в `app/services/llm_parser.py`: инициализация `AsyncOpenAI` с `base_url` OpenRouter, вызов `chat.completions.create` с `temperature=0.1` и `response_format={"type": "json_object"}`, таймаут 15 секунд
- [x] 3.2 Добавить валидацию ответа LLM через `ParsedEvent.model_validate_json()`
- [x] 3.3 Реализовать retry при HTTP 429/5xx — до 3 попыток с экспоненциальным backoff (1s, 2s, 4s)
- [x] 3.4 Реализовать одну повторную попытку при невалидном JSON с усиленной инструкцией
- [x] 3.5 Добавить логирование: model, input_tokens, output_tokens, duration_ms при успехе; model, error_type, duration_ms при ошибке

## 4. Интеграция с хендлерами

- [x] 4.1 Обновить `app/bot/handlers/event.py`: заменить `parse_event_text()` на `llm_parser.parse_event()`, добавить `bot.send_chat_action(typing)` перед вызовом, обработать `ParseError` с разными сообщениями по типу ошибки
- [x] 4.2 Обновить `app/bot/callbacks/event_confirm.py`: заменить `parse_event_text()` на `llm_parser.parse_event()` в `handle_event_edit`, убрать `FORMAT_HINT` из сообщения при нажатии «Изменить»
- [x] 4.3 Удалить `FORMAT_HINT` из `app/bot/formatting.py` и все ссылки на него в импортах

## 5. Проверка

- [x] 5.1 Проверить что `openai` есть в `requirements.txt` (уже должен быть)
- [x] 5.2 Убедиться что бот стартует без ошибок: `docker compose up --build`
