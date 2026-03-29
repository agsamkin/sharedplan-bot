## MODIFIED Requirements

### Requirement: REST API для событий

Система ДОЛЖНА предоставлять эндпоинты для работы с событиями пространства.

#### Scenario: Получение списка событий пространства
- **WHEN** `GET /api/spaces/:space_id/events` от участника пространства
- **THEN** возвращается JSON-объект `{ "events": [...], "total_count": N }`, где `events` — массив будущих событий (по умолчанию до 50, максимум 100), отсортированных по `event_date ASC, event_time ASC NULLS FIRST`, с полями: `id`, `title`, `event_date`, `event_time`, `created_by`, `creator_name`, `is_owner`; `total_count` — общее количество предстоящих событий в пространстве (без учёта лимита)

#### Scenario: Получение списка событий с параметром limit
- **WHEN** `GET /api/spaces/:space_id/events?limit=20` от участника пространства
- **THEN** возвращается JSON-объект с массивом `events` длиной не более 20, `total_count` отражает полное количество предстоящих событий

#### Scenario: Параметр limit превышает максимум
- **WHEN** `GET /api/spaces/:space_id/events?limit=500` от участника пространства
- **THEN** `limit` ограничивается значением 100, возвращается не более 100 событий

#### Scenario: Диагностическое логирование запроса событий
- **WHEN** любой запрос `GET /api/spaces/:space_id/events` обрабатывается
- **THEN** в лог записывается: `user_id`, `space_id`, количество возвращённых событий, `total_count`

#### Scenario: Получение списка событий чужого пространства
- **WHEN** `GET /api/spaces/:space_id/events` от пользователя, не состоящего в пространстве
- **THEN** сервер отвечает `403 Forbidden`

#### Scenario: Получение карточки события
- **WHEN** `GET /api/events/:event_id` от участника пространства события
- **THEN** возвращается JSON с полями: `id`, `title`, `event_date`, `event_time`, `created_by`, `creator_name`, `space_id`, `space_name`, `is_owner`, `created_at`

#### Scenario: Редактирование события владельцем
- **WHEN** `PUT /api/events/:event_id` с телом `{"title": "Новое название"}` от владельца события
- **THEN** событие обновляется, неотправленные напоминания пересоздаются (при изменении даты/времени), участники получают уведомление через бота, возвращается обновлённое событие

#### Scenario: Редактирование чужого события
- **WHEN** `PUT /api/events/:event_id` от пользователя, не являющегося владельцем
- **THEN** сервер отвечает `403 Forbidden`

#### Scenario: Удаление события владельцем
- **WHEN** `DELETE /api/events/:event_id` от владельца события
- **THEN** событие удаляется, связанные напоминания удаляются каскадно, участники получают уведомление через бота, возвращается `204 No Content`

#### Scenario: Удаление чужого события
- **WHEN** `DELETE /api/events/:event_id` от пользователя, не являющегося владельцем
- **THEN** сервер отвечает `403 Forbidden`

#### Scenario: Событие не найдено
- **WHEN** `GET /api/events/:event_id` с несуществующим ID
- **THEN** сервер отвечает `404 Not Found`
