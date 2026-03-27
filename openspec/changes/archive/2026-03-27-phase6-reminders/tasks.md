## 1. Сервисный слой напоминаний

- [x] 1.1 Создать `app/services/reminder_service.py` с функцией `create_reminders_for_event(session, event, space_id)` — итерация по участникам пространства, чтение `reminder_settings`, расчёт `remind_at`, создание записей `scheduled_reminders` (фильтрация прошедших, обработка событий без времени)
- [x] 1.2 Добавить в `reminder_service.py` функцию `get_due_reminders(session, limit=50)` — запрос неотправленных напоминаний с наступившим `remind_at`, загрузка связанных событий и пространств
- [x] 1.3 Добавить в `reminder_service.py` функцию `mark_sent(session, reminder_id)` — пометка напоминания как отправленного
- [x] 1.4 Добавить в `reminder_service.py` функцию `format_reminder_message(event_title, event_date, event_time, space_name, reminder_type)` — форматирование текста Telegram-сообщения напоминания с relative_label

## 2. Создание напоминаний при публикации события

- [x] 2.1 Модифицировать `app/bot/callbacks/event_confirm.py` — после `event_service.create_event()` вызвать `reminder_service.create_reminders_for_event()` в той же сессии

## 3. Планировщик APScheduler

- [x] 3.1 Создать `app/scheduler/jobs.py` с функцией `process_due_reminders(bot, session_factory)` — на каждом тике: создать сессию, запросить наступившие напоминания, отправить сообщения, пометить как отправленные, обработать ошибки
- [x] 3.2 Модифицировать `app/main.py` — импортировать и запустить `AsyncIOScheduler`, зарегистрировать `process_due_reminders` с интервалом из `settings.REMINDER_CHECK_INTERVAL_SECONDS`, передать `bot` и `async_session`

## 4. Команда /reminders и toggle-интерфейс

- [x] 4.1 Создать `app/bot/keyboards/reminder_settings.py` — функция `reminder_settings_keyboard(settings: dict)` возвращающая `InlineKeyboardMarkup` с 6 toggle-кнопками (☑/☐) и callback data `reminder_toggle:{key}`
- [x] 4.2 Создать `app/bot/handlers/reminders.py` — обработчик команды `/reminders`, чтение `reminder_settings` пользователя из БД, отправка сообщения с клавиатурой
- [x] 4.3 Создать `app/bot/callbacks/reminder_toggle.py` — обработчик callback `reminder_toggle:*`, инверсия ключа в `reminder_settings`, обновление JSONB в БД, `edit_message_reply_markup`

## 5. Интеграция

- [x] 5.1 Зарегистрировать роутеры `reminders.router` и `reminder_toggle.router` в `app/main.py`
- [x] 5.2 Создать файл `app/scheduler/__init__.py` (пустой, для пакета)
