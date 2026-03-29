## 1. Конфигурация

- [x] 1.1 Сделать `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `NEXARA_API_KEY` опциональными в `app/config.py` (`Optional[str] = None`)
- [x] 1.2 Обновить `.env.example` — пометить API-ключи как «(опционально)»

## 2. Сервисы — ранняя проверка доступности

- [x] 2.1 В `app/services/speech_to_text.py`: добавить проверку `settings.NEXARA_API_KEY is None` в начале `transcribe()` с выбросом `TranscriptionError(error_type="service_disabled")`
- [x] 2.2 В `app/services/llm_parser.py`: добавить проверку `settings.OPENROUTER_API_KEY is None` в начале `parse_event()` с выбросом `ParseError(error_type="service_disabled")`

## 3. Сообщения об ошибках

- [x] 3.1 В `app/bot/formatting.py`: добавить сообщение для `service_disabled` в `STT_ERROR_MESSAGES` — «Функция голосовых сообщений отключена. Напиши текстом или создай событие в приложении.»
- [x] 3.2 В `app/bot/formatting.py`: добавить сообщение для `service_disabled` в `PARSE_ERROR_MESSAGES` — «Автоматическое распознавание событий отключено. Создай событие вручную в приложении.»

## 4. Хендлеры — обработка отключённых функций

- [x] 4.1 В `app/bot/handlers/event.py`: при `ParseError` с типом `service_disabled` добавить inline-кнопку «Открыть приложение» (если `MINI_APP_URL` задан)
- [x] 4.2 В `app/bot/handlers/voice.py`: при `ParseError` с типом `service_disabled` от `parse_event()` показать транскрипцию и предложить Mini App

## 5. Логирование при старте

- [x] 5.1 В `app/main.py`: добавить логирование доступности STT и LLM после проверки Telegram-токена (INFO если включён, WARNING если отключён)

## 6. Тестирование

- [x] 6.1 Проверить запуск бота без API-ключей (приложение стартует)
- [x] 6.2 Проверить отправку голосового сообщения без NEXARA_API_KEY (сообщение об отключении)
- [x] 6.3 Проверить отправку текста без OPENROUTER_API_KEY (сообщение об отключении + кнопка Mini App)
- [x] 6.4 Проверить полный флоу с обоими ключами (работает как раньше)
