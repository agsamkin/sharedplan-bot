## 1. Сервисный слой

- [x] 1.1 Добавить функцию `find_conflicting_events(session, space_id, event_date, event_time, exclude_event_id=None)` в `app/services/event_service.py` — запрос к таблице `events` с фильтром по `space_id`, `event_date`, `event_time` в окне +-2 часа, исключение NULL-времени и опционально `exclude_event_id`

## 2. Форматирование

- [x] 2.1 Добавить функцию `format_conflict_warning(conflicts: list[Event])` в `app/bot/formatting.py` — формирует текст предупреждения с перечнем конфликтующих событий

## 3. Интеграция в бота

- [x] 3.1 Модифицировать `_show_confirmation_or_past_warning` в `app/bot/handlers/event.py` — добавить вызов `find_conflicting_events` и передачу результата в `format_confirmation` (для событий с временем, если дата не в прошлом)
- [x] 3.2 Модифицировать `format_confirmation` в `app/bot/formatting.py` — принять опциональный параметр `conflict_warning: str | None` и добавить его перед основной карточкой
- [x] 3.3 Модифицировать callback `on_space_select` в `app/bot/callbacks/space_select.py` — добавить проверку конфликтов при показе подтверждения после выбора пространства
- [x] 3.4 Модифицировать callback `on_past_date_confirm` — при подтверждении прошедшей даты показать карточку подтверждения с проверкой конфликтов

## 4. Mini App

- [x] 4.1 Добавить поле `conflicts` в ответ PUT `/api/events/{event_id}` в `mini_app/backend/routes/events.py` — при изменении даты/времени вызвать `find_conflicting_events` и вернуть массив конфликтов в ответе
