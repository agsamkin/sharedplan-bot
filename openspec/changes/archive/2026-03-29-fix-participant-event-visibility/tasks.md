## 1. Backend: сервис событий

- [x] 1.1 В `app/services/event_service.py`: добавить функцию `count_upcoming_events(session, space_id) -> int` — COUNT предстоящих событий без лимита (та же фильтрация по дате/времени, что в `get_upcoming_events`)
- [x] 1.2 В `app/services/event_service.py`: изменить `get_upcoming_events` — сделать параметр `limit` обязательным (убрать default=10), чтобы вызывающий код явно указывал лимит

## 2. Backend: API эндпоинт

- [x] 2.1 В `mini_app/backend/routes/events.py` (`list_events`): добавить парсинг query-параметра `limit` (default=50, max=100, min=1)
- [x] 2.2 В `list_events`: вызвать `count_upcoming_events` для получения `total_count`
- [x] 2.3 В `list_events`: изменить формат ответа с массива на `{ "events": [...], "total_count": N }`
- [x] 2.4 В `list_events`: добавить `logger.info` с `user_id`, `space_id`, кол-вом событий и `total_count`

## 3. Frontend: обновление API-клиента

- [x] 3.1 В `mini_app/frontend/src/api/events.ts`: обновить тип ответа `getSpaceEvents` — вернуть `{ events: SpaceEvent[], total_count: number }` вместо `SpaceEvent[]`

## 4. Frontend: обновление SpaceDetailPage

- [x] 4.1 В `mini_app/frontend/src/pages/SpaceDetailPage.tsx`: обновить `fetchData` для работы с новым форматом ответа (деструктуризация `{ events, total_count }`)
- [x] 4.2 Обновить заголовок секции событий — использовать `totalCount` вместо `events.length`

## 5. Тесты

- [x] 5.1 Написать тест: `GET /api/spaces/:id/events` возвращает объект с `events` и `total_count`
- [x] 5.2 Написать тест: параметр `limit` ограничивает количество событий, `total_count` остаётся полным
- [x] 5.3 Написать тест: `limit` > 100 ограничивается до 100
- [x] 5.4 Убедиться что существующие тесты проходят после изменений
