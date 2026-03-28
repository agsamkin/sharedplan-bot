## ADDED Requirements

### Requirement: Создание события через API
Эндпоинт `POST /api/spaces/:space_id/events` SHALL создавать новое событие в указанном пространстве. Тело запроса: `{"title": "<string>", "event_date": "<YYYY-MM-DD>", "event_time": "<HH:MM>" | null}`. Хендлер SHALL проверять членство пользователя в пространстве, валидировать данные, вызывать `event_service.create_event()`, создавать напоминания через `event_service.create_reminders_for_event()`, отправлять уведомления участникам через бота.

#### Scenario: Успешное создание события
- **WHEN** `POST /api/spaces/:space_id/events` с телом `{"title": "Ужин", "event_date": "2026-04-10", "event_time": "19:00"}` от участника пространства
- **THEN** создаётся событие, создаются напоминания для участников, отправляются уведомления через бота, возвращается `201 Created` с JSON: `{"id": "<uuid>", "title": "Ужин", "event_date": "2026-04-10", "event_time": "19:00", "created_by": <user_id>, "creator_name": "<name>"}`

#### Scenario: Создание события без времени
- **WHEN** `POST /api/spaces/:space_id/events` с телом `{"title": "День рождения", "event_date": "2026-04-15", "event_time": null}` от участника пространства
- **THEN** создаётся событие с `event_time = NULL`, напоминания создаются только для интервала `1d`

#### Scenario: Создание события не-участником пространства
- **WHEN** `POST /api/spaces/:space_id/events` от пользователя, не состоящего в пространстве
- **THEN** сервер отвечает `403 Forbidden`

#### Scenario: Пустое название
- **WHEN** `POST /api/spaces/:space_id/events` с телом `{"title": "  ", "event_date": "2026-04-10"}`
- **THEN** сервер отвечает `400 Bad Request` с телом `{"error": "Название не может быть пустым"}`

#### Scenario: Название слишком длинное
- **WHEN** `POST /api/spaces/:space_id/events` с телом `{"title": "<string > 500 символов>", "event_date": "2026-04-10"}`
- **THEN** сервер отвечает `400 Bad Request` с телом `{"error": "Название слишком длинное (макс. 500 символов)"}`

#### Scenario: Отсутствует обязательное поле
- **WHEN** `POST /api/spaces/:space_id/events` с телом `{"title": "Ужин"}`
- **THEN** сервер отвечает `400 Bad Request` с телом `{"error": "Поле event_date обязательно"}`

#### Scenario: Невалидный формат даты
- **WHEN** `POST /api/spaces/:space_id/events` с телом `{"title": "Ужин", "event_date": "не-дата"}`
- **THEN** сервер отвечает `400 Bad Request` с телом `{"error": "Невалидный формат даты"}`

#### Scenario: Уведомление участников при создании через API
- **WHEN** событие успешно создано через API в пространстве с 4 участниками
- **THEN** 3 участника (кроме создателя) получают уведомление через Telegram бота

#### Scenario: Ошибка уведомления не блокирует создание
- **WHEN** событие создано, но уведомление одному участнику не удалось отправить
- **THEN** ошибка логируется, API возвращает `201 Created`
