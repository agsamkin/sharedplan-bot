## 1. Startup-проверки

- [x] 1.1 Добавить проверку связности с PostgreSQL (`SELECT 1`) в `main.py` — после создания engine, до миграций. При ошибке — `sys.exit(1)` с описательным сообщением
- [x] 1.2 Переупорядочить startup: (1) PostgreSQL check, (2) Alembic миграции, (3) `bot.get_me()` для проверки токена. Убедиться что `get_me` уже вызывается; добавить обработку ошибки с `sys.exit(1)`
- [x] 1.3 Обернуть весь startup-блок в try/except для перехвата непредвиденных ошибок запуска с логированием

## 2. Middleware обновления профиля

- [x] 2.1 Создать `app/bot/middlewares/user_profile.py` с классом `UserProfileMiddleware`, который при каждом сообщении/callback вызывает upsert пользователя (first_name, username) через существующий `get_or_create_user()`
- [x] 2.2 Зарегистрировать `UserProfileMiddleware` в `main.py` после `DbSessionMiddleware`

## 3. Валидация ввода

- [x] 3.1 Добавить проверку длины текста (1–1000 символов) в `app/bot/handlers/event.py` перед вызовом `parse_event()`. При превышении — сообщение пользователю
- [x] 3.2 Добавить аналогичную проверку длины транскрипции в `app/bot/handlers/voice.py` после получения транскрипции и перед вызовом `parse_event()`
- [x] 3.3 Добавить Pydantic-валидатор в `ParsedEvent` (`app/services/llm_parser.py`): `event_date` не более 2 лет в будущее от текущей даты. При нарушении — `ValidationError` → `ParseError(invalid_json)`

## 4. Предупреждение о прошедшей дате

- [x] 4.1 Создать inline-клавиатуру для подтверждения прошедшей даты в `app/bot/keyboards/` (или расширить `confirm.py`): кнопки `[✅ Всё равно создать]` callback=`event_past_confirm` и `[❌ Отмена]` callback=`event_past_cancel`
- [x] 4.2 Добавить проверку `event_date < today` в `app/bot/handlers/event.py` после парсинга: если дата прошла — показать предупреждающую карточку вместо стандартной
- [x] 4.3 Добавить аналогичную проверку в `app/bot/handlers/voice.py` после парсинга транскрипции
- [x] 4.4 Добавить callback-обработчик `event_past_confirm` — при подтверждении показывает стандартную карточку подтверждения события
- [x] 4.5 Добавить callback-обработчик `event_past_cancel` — при отмене обновляет сообщение на «Отменено»
- [x] 4.6 Зарегистрировать новые callback-обработчики в `main.py`

## 5. Логирование

- [x] 5.1 Стандартизировать формат логирования в `main.py`: `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`
- [x] 5.2 Добавить `logger.info` в начало каждого command-handler'а: `/start`, `/help`, `/newspace`, `/spaces`, `/space_info`, `/events`, `/reminders`, `/kick`, `/delete_space` — формат: `"/{command} user_id={id}"`
- [x] 5.3 Добавить `logger.info("event_create user_id=%d", ...)` в handler событий (event.py, voice.py)
- [x] 5.4 Убедиться что все ошибки отправки Telegram логируются с `user_id` и `error_type` — проверить start.py, event_confirm.py, jobs.py

## 6. Проверка и доработка edge cases

- [x] 6.1 Проверить обработку пустой транскрипции от Nexara (уже есть `empty_result`) — убедиться что пользователь получает понятное сообщение
- [x] 6.2 Проверить и унифицировать обработку заблокированного бота при отправке уведомлений — все try/except ДОЛЖНЫ логировать `user_id` и тип ошибки
- [x] 6.3 Убедиться что ни одна ошибка не приводит к traceback в чате пользователя — проверить все handlers на наличие верхнеуровневого try/except
