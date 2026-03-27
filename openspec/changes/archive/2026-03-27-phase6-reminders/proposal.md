## Why

После публикации события участники не получают напоминаний — они должны сами помнить о предстоящих событиях. Фаза 6 добавляет автоматические персонализированные напоминания: при публикации события система создаёт предвычисленные записи напоминаний для каждого участника, фоновый планировщик отправляет их в нужное время, а каждый пользователь настраивает интервалы через интерактивный интерфейс.

## What Changes

- **Планировщик напоминаний**: APScheduler `AsyncIOScheduler` запускается вместе с ботом, интервальная задача `process_due_reminders` каждые 30 секунд выбирает наступившие напоминания и отправляет Telegram-сообщения
- **Создание напоминаний при публикации события**: при подтверждении события для каждого участника пространства создаются записи `scheduled_reminders` на основе их `reminder_settings`
- **Команда `/reminders`**: интерактивный интерфейс с toggle-кнопками для настройки персональных интервалов напоминаний (6 интервалов: 1d, 2h, 1h, 30m, 15m, 0m)
- **Сервисный слой `reminder_service.py`**: расчёт `remind_at`, запрос наступивших напоминаний, отправка, форматирование сообщений
- **Inline-клавиатура и callback-обработчик**: `keyboards/reminder_settings.py` + `callbacks/reminder_toggle.py`

## Capabilities

### New Capabilities
- `reminder-scheduler`: Фоновая задача APScheduler для обработки и отправки наступивших напоминаний — запрос из `scheduled_reminders`, отправка Telegram-сообщений, пометка как отправленных
- `reminder-settings`: Команда `/reminders` с toggle-интерфейсом для персонализации интервалов напоминаний, callback-обработка переключения, клавиатура с состояниями ☑/☐

### Modified Capabilities
- `event-creation`: При подтверждении события ДОЛЖНЫ создаваться записи `scheduled_reminders` для всех участников пространства (сейчас spec явно указывает «НЕ создаются»)

## Impact

- **Новые файлы**: `services/reminder_service.py`, `scheduler/jobs.py`, `bot/handlers/reminders.py`, `bot/keyboards/reminder_settings.py`, `bot/callbacks/reminder_toggle.py`
- **Изменяемые файлы**: `app/main.py` (запуск APScheduler), `services/event_service.py` (создание напоминаний при публикации), `bot/handlers/event.py` (вызов создания напоминаний через сервис)
- **Зависимости**: `apscheduler` (уже в requirements.txt)
- **БД**: Таблица `scheduled_reminders` и поле `users.reminder_settings` уже созданы в Фазе 1 — новых миграций не требуется
