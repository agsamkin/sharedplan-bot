## 1. Доработка функций форматирования

- [x] 1.1 Переработать `format_event_edited_notification` в `app/bot/formatting.py` — принимать список изменений `changes: list[tuple[str, str, str]]` (field_label, old_value, new_value) вместо одного поля; генерировать строку `🔄` для каждого изменения
- [x] 1.2 Доработать `format_event_deleted_notification` в `app/bot/formatting.py` — добавить опциональные параметры `event_date` и `event_time` для отображения даты/времени удалённого события в формате `format_date_short_with_weekday`

## 2. Уведомление при редактировании в Mini App backend

- [x] 2.1 В `update_event` handler (`mini_app/backend/routes/events.py`) — сохранить старые значения полей (title, event_date, event_time) ДО вызова `event_service.update_event`
- [x] 2.2 Собрать список изменений: для каждого изменённого поля сформировать tuple (label, old_formatted, new_formatted) с использованием `format_date_short_with_weekday` для дат и `HH:MM` для времени
- [x] 2.3 Заменить инлайн-строку `f"📝 Событие изменено: {updated_event.title}"` на вызов обновлённой `format_event_edited_notification` с передачей space_name, title, списка изменений и editor_name

## 3. Уведомление при удалении в Mini App backend

- [x] 3.1 В `delete_event` handler (`mini_app/backend/routes/events.py`) — получить space_name и editor_name перед отправкой уведомления
- [x] 3.2 Заменить инлайн-строку `f"🗑 Событие удалено: {event.title}"` на вызов обновлённой `format_event_deleted_notification` с передачей space_name, title, editor_name, event_date, event_time

## 4. Проверка

- [x] 4.1 Убедиться, что при изменении одного поля (например, только даты) уведомление содержит одну строку `🔄` с правильным форматом
- [x] 4.2 Убедиться, что при изменении нескольких полей одновременно отправляется одно сообщение со всеми изменениями
- [x] 4.3 Убедиться, что уведомление об удалении содержит дату/время и название пространства
