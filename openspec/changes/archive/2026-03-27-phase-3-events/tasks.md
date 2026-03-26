## 1. Сервисный слой

- [x] 1.1 Создать `app/services/event_service.py`: функция `parse_event_text(text) → ParsedEvent` — парсинг структурированного формата `название, ДД.ММ.ГГГГ, ЧЧ:ММ` с валидацией и обрезкой пробелов
- [x] 1.2 Добавить в `event_service.py` функцию `create_event(session, space_id, title, event_date, event_time, created_by, raw_input) → Event` — создание записи в таблице `events`
- [x] 1.3 Добавить в `event_service.py` функцию `get_upcoming_events(session, space_id, limit=10)` — получение будущих событий (event_date >= сегодня), сортировка по date ASC, time ASC NULLS FIRST

## 2. Клавиатуры и FSM-состояния

- [x] 2.1 Создать `app/bot/keyboards/confirm.py` (или расширить существующий): клавиатура подтверждения события с кнопками `✅ Да` (`event_confirm`), `✏️ Изменить` (`event_edit`), `❌ Отмена` (`event_cancel`)
- [x] 2.2 Создать `app/bot/states/create_event.py`: FSM-состояния `CreateEvent` — `waiting_for_space`, `waiting_for_confirm`, `waiting_for_edit`

## 3. Обработчик создания событий

- [x] 3.1 Создать `app/bot/handlers/event.py`: обработчик текстовых сообщений (фильтр `NotCommandFilter`) — парсинг текста, определение пространства (одно → авто, несколько → выбор), показ карточки подтверждения
- [x] 3.2 Обработка выбора пространства: добавить action `"event"` в callback `space_select` — сохранение space_id в FSM, показ карточки подтверждения
- [x] 3.3 Обработка случая «пользователь не в пространстве» — ответ с предложением `/newspace`

## 4. Callback-обработчики подтверждения

- [x] 4.1 Создать `app/bot/callbacks/event_confirm.py`: обработчик `event_confirm` — сохранение события через `event_service.create_event()`, обновление карточки
- [x] 4.2 Обработчик `event_cancel` — обновление карточки сообщением «Отменено», очистка FSM
- [x] 4.3 Обработчик `event_edit` — отправка инструкции по формату, переход FSM в состояние `waiting_for_edit`
- [x] 4.4 Обработчик повторного ввода в состоянии `waiting_for_edit` — повторный парсинг и обновлённая карточка

## 5. Уведомления участников

- [x] 5.1 Добавить в `event_service.py` (или handler) логику уведомления: после сохранения — получить участников пространства, отправить каждому (кроме создателя) сообщение формата `📅 Новое событие в «{space}»!`. Каждая отправка в try/except с логированием ошибок.

## 6. Команда /events

- [x] 6.1 Создать `app/bot/handlers/events_list.py`: команда `/events` — выбор пространства (авто или inline-клавиатура), запрос событий через `event_service.get_upcoming_events()`, форматирование с относительными датами (сегодня/завтра), обработка событий без времени
- [x] 6.2 Добавить action `"events"` в callback `space_select` для выбора пространства при `/events`

## 7. Регистрация роутеров

- [x] 7.1 Зарегистрировать роутеры `event.py`, `events_list.py`, `event_confirm.py` в `app/main.py` — подключить к диспатчеру
