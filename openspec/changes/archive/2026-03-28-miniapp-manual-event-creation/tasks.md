## 1. Backend API — POST-эндпоинт создания события

- [x] 1.1 Добавить хендлер `create_event_handler` в `app/web/handlers/events.py` для `POST /api/spaces/:space_id/events` с валидацией тела запроса (title непустой, <= 500 символов; event_date обязательна, валидный формат YYYY-MM-DD; event_time опционален, формат HH:MM)
- [x] 1.2 Добавить проверку членства пользователя в пространстве (403 Forbidden для не-участников)
- [x] 1.3 Вызвать `event_service.create_event()` и `event_service.create_reminders_for_event()`, затем отправить уведомления участникам через бота (переиспользовать `notify_space_members`)
- [x] 1.4 Зарегистрировать роут `POST /api/spaces/{space_id}/events` в `app/web/routes.py`

## 2. Frontend — экран создания события

- [x] 2.1 Создать компонент `EventCreateScreen` в `mini-app/src/screens/EventCreateScreen.jsx` с формой: input название (autoFocus, placeholder «Ужин с друзьями»), input type="date" дата, input type="time" время (необязательно), кнопка «Создать событие»
- [x] 2.2 Реализовать валидацию формы: кнопка disabled при пустом названии или отсутствии даты, ограничение 500 символов
- [x] 2.3 Реализовать предупреждение о прошедшей дате (оранжевый текст под полем даты)
- [x] 2.4 Реализовать предупреждение о конфликтах по времени (±2 часа, используя загруженный список событий пространства)
- [x] 2.5 Реализовать отправку `POST /api/spaces/:space_id/events`, блокировку кнопки на время запроса, навигацию назад и Toast «Событие создано» при успехе, Toast с ошибкой при неудаче

## 3. Frontend — интеграция в навигацию и Space Detail

- [x] 3.1 Добавить роут `/spaces/:id/events/new` в React Router (`App.jsx` или `routes.jsx`)
- [x] 3.2 Добавить кнопку «Добавить» (иконка + текст) в заголовок секции событий на экране `SpaceDetailScreen`, с навигацией на `/spaces/:id/events/new`
- [x] 3.3 Обновить сообщение пустого состояния (убрать упоминание бота, т.к. теперь можно создать из Mini App)
