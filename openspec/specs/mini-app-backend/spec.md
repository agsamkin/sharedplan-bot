# Capability: mini-app-backend

## Purpose

REST API бэкенд для Telegram Mini App: aiohttp web server, авторизация через initData, DB middleware, эндпоинты для пространств, событий и настроек напоминаний, уведомления участников через бота.

## Requirements

### Requirement: aiohttp web server интегрированный с ботом

Система ДОЛЖНА запускать aiohttp web server в том же asyncio event loop, что и aiogram бот. Web server ДОЛЖЕН слушать на настраиваемом порту (env `MINI_APP_PORT`, default `8080`). Сервер ДОЛЖЕН раздавать REST API на `/api/*` и статические файлы фронтенда на `/`.

#### Scenario: Запуск web server вместе с ботом
- **WHEN** приложение стартует через `python -m app.main`
- **THEN** aiohttp web server запускается на порту `MINI_APP_PORT` одновременно с aiogram long-polling

#### Scenario: API и статика на одном сервере
- **WHEN** браузер запрашивает `GET /`
- **THEN** возвращается `index.html` из директории собранного фронтенда

#### Scenario: API запрос
- **WHEN** клиент отправляет запрос на `/api/spaces`
- **THEN** запрос обрабатывается соответствующим API-хендлером

### Requirement: Авторизация через Telegram initData

Каждый запрос к `/api/*` ДОЛЖЕН содержать заголовок `Authorization: tma <initData>`. Бэкенд ДОЛЖЕН валидировать HMAC-SHA256 подпись initData используя `TELEGRAM_BOT_TOKEN`. При невалидной подписи — ответ `401 Unauthorized`.

#### Scenario: Валидный initData
- **WHEN** клиент отправляет запрос с валидным `Authorization: tma <initData>`
- **THEN** запрос обрабатывается, user_id извлекается из initData

#### Scenario: Невалидная подпись
- **WHEN** клиент отправляет запрос с невалидной подписью initData
- **THEN** сервер отвечает `401 Unauthorized` с телом `{"error": "Invalid initData signature"}`

#### Scenario: Отсутствует заголовок Authorization
- **WHEN** клиент отправляет запрос без заголовка `Authorization`
- **THEN** сервер отвечает `401 Unauthorized` с телом `{"error": "Authorization header required"}`

#### Scenario: Просроченный initData
- **WHEN** initData содержит `auth_date` старше 1 часа
- **THEN** сервер отвечает `401 Unauthorized` с телом `{"error": "initData expired"}`

### Requirement: DB-сессия middleware для API

Каждый API-запрос ДОЛЖЕН получать async SQLAlchemy сессию. Сессия ДОЛЖНА коммититься при успешном ответе (2xx) и откатываться при ошибке.

#### Scenario: Успешный API-запрос
- **WHEN** API-хендлер обрабатывает запрос без ошибок
- **THEN** DB-сессия коммитится и изменения сохраняются

#### Scenario: Ошибка в API-хендлере
- **WHEN** API-хендлер выбрасывает исключение
- **THEN** DB-сессия откатывается, клиент получает `500 Internal Server Error`

### Requirement: REST API для событий

Система ДОЛЖНА предоставлять эндпоинты для работы с событиями пространства.

#### Scenario: Получение списка событий пространства
- **WHEN** `GET /api/spaces/:space_id/events` от участника пространства
- **THEN** возвращается JSON-объект `{ "events": [...], "total_count": N }`, где `events` — массив будущих событий (по умолчанию до 50, максимум 100), отсортированных по `event_date ASC, event_time ASC NULLS FIRST`, с полями: `id`, `title`, `event_date`, `event_time`, `created_by`, `creator_name`, `is_owner`, `recurrence_rule`, `parent_event_id`; `total_count` — общее количество предстоящих событий в пространстве (без учёта лимита). Дочерние вхождения (`parent_event_id != null`) НЕ возвращаются в списке — только родительские события и одноразовые

#### Scenario: Список событий с повторяющимися
- **WHEN** GET запрос списка событий пространства
- **THEN** возвращаются только родительские и одноразовые события (без дочерних вхождений), каждое с полем `recurrence_rule`

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
- **THEN** возвращается JSON с полями: `id`, `title`, `event_date`, `event_time`, `created_by`, `creator_name`, `space_id`, `space_name`, `is_owner`, `created_at`, `recurrence_rule`, `parent_event_id`

#### Scenario: Детали повторяющегося события
- **WHEN** GET запрос к повторяющемуся событию
- **THEN** ответ содержит `recurrence_rule: "weekly"` (или другое значение)

#### Scenario: Редактирование события владельцем
- **WHEN** `PUT /api/events/:event_id` с телом `{"title": "Новое название"}` от владельца события
- **THEN** событие обновляется, неотправленные напоминания пересоздаются (при изменении даты/времени), участники получают уведомление через бота, возвращается обновлённое событие с `recurrence_rule`

#### Scenario: Изменение правила повторения
- **WHEN** PUT с `{"recurrence_rule": "monthly"}` для события с текущим `recurrence_rule: "weekly"`
- **THEN** будущие дочерние вхождения пересоздаются по правилу `monthly`, возвращается обновлённое событие

#### Scenario: Отключение повторения
- **WHEN** PUT с `{"recurrence_rule": null}` для повторяющегося события
- **THEN** все дочерние вхождения удаляются, событие становится одноразовым

#### Scenario: Редактирование чужого события
- **WHEN** `PUT /api/events/:event_id` от пользователя, не являющегося владельцем
- **THEN** сервер отвечает `403 Forbidden`

#### Scenario: Удаление события владельцем
- **WHEN** `DELETE /api/events/:event_id` от владельца события
- **THEN** событие удаляется с каскадным удалением напоминаний и дочерних вхождений (через FK ON DELETE CASCADE), участники получают уведомление через бота, возвращается `204 No Content`

#### Scenario: Удаление повторяющегося события
- **WHEN** DELETE запрос к повторяющемуся событию
- **THEN** удаляется родительское событие, все дочерние вхождения и их напоминания каскадно, возвращается 204

#### Scenario: Удаление чужого события
- **WHEN** `DELETE /api/events/:event_id` от пользователя, не являющегося владельцем
- **THEN** сервер отвечает `403 Forbidden`

#### Scenario: Событие не найдено
- **WHEN** `GET /api/events/:event_id` с несуществующим ID
- **THEN** сервер отвечает `404 Not Found`

### Requirement: Создание события через API

Создание события. Валидация: title (не пустой, ≤500), event_date (обязательный, YYYY-MM-DD), event_time (обязательный, HH:MM), **recurrence_rule (опциональный — daily, weekly, biweekly, monthly, yearly или null/отсутствует)**. Создать запись `events` с `recurrence_rule`. Если `recurrence_rule != null` — сгенерировать дочерние вхождения на 60 дней вперёд, создать напоминания для каждого вхождения. Уведомить участников. Вернуть 201 с созданным событием включая поле `recurrence_rule`.

#### Scenario: Создание повторяющегося события через API
- **WHEN** POST с `{"title": "Встреча", "event_date": "2026-04-01", "event_time": "15:00", "recurrence_rule": "weekly"}`
- **THEN** создаётся родительское событие и дочерние вхождения, возвращается 201 с `recurrence_rule: "weekly"`

#### Scenario: Создание одноразового события (обратная совместимость)
- **WHEN** POST без поля `recurrence_rule` или с `recurrence_rule: null`
- **THEN** создаётся одноразовое событие, поведение идентично текущему

#### Scenario: Невалидное значение recurrence_rule
- **WHEN** POST с `recurrence_rule: "every_3_days"`
- **THEN** возвращается 400 с ошибкой валидации

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

### Requirement: Создание пространства через API

Эндпоинт `POST /api/spaces` ДОЛЖЕН создавать новое пространство. Тело запроса: `{"name": "<string>"}`. Имя ДОЛЖНО валидироваться: не пустое, не более 255 символов (после trim). Хэндлер ДОЛЖЕН вызывать `space_service.create_space(session, user_id, name)`. Ответ: `201 Created` с JSON: `{"id": "<uuid>", "name": "<string>", "invite_code": "<string>", "role": "admin", "member_count": 1}`.

#### Scenario: Успешное создание пространства
- **WHEN** `POST /api/spaces` с телом `{"name": "Семья"}` от авторизованного пользователя
- **THEN** создаётся пространство, пользователь назначается администратором, возвращается `201 Created` с данными пространства

#### Scenario: Пустое название
- **WHEN** `POST /api/spaces` с телом `{"name": "  "}` от авторизованного пользователя
- **THEN** сервер отвечает `400 Bad Request` с телом `{"error": "Название не может быть пустым"}`

#### Scenario: Слишком длинное название
- **WHEN** `POST /api/spaces` с телом `{"name": "<string длиннее 255 символов>"}` от авторизованного пользователя
- **THEN** сервер отвечает `400 Bad Request` с телом `{"error": "Название слишком длинное (макс. 255 символов)"}`

#### Scenario: Отсутствует поле name
- **WHEN** `POST /api/spaces` с телом `{}` от авторизованного пользователя
- **THEN** сервер отвечает `400 Bad Request` с телом `{"error": "Поле name обязательно"}`

### Requirement: REST API для пространств

Система ДОЛЖНА предоставлять эндпоинты для работы с пространствами.

#### Scenario: Получение списка пространств пользователя
- **WHEN** `GET /api/spaces` от авторизованного пользователя
- **THEN** возвращается JSON-массив пространств пользователя с полями: `id`, `name`, `role`, `member_count`, `invite_code`

#### Scenario: Получение информации о пространстве
- **WHEN** `GET /api/spaces/:space_id` от участника пространства
- **THEN** возвращается JSON с полями: `id`, `name`, `invite_code`, `created_by`, `members` (массив: `user_id`, `first_name`, `username`, `role`, `joined_at`)

#### Scenario: Удаление пространства администратором
- **WHEN** `DELETE /api/spaces/:space_id` от администратора пространства
- **THEN** пространство удаляется каскадно (user_spaces, events, reminders), возвращается `204 No Content`

#### Scenario: Удаление пространства не-администратором
- **WHEN** `DELETE /api/spaces/:space_id` от участника с ролью member
- **THEN** сервер отвечает `403 Forbidden`

#### Scenario: Удаление участника из пространства
- **WHEN** `DELETE /api/spaces/:space_id/members/:user_id` от администратора
- **THEN** участник удаляется из пространства, возвращается `204 No Content`

#### Scenario: Администратор пытается удалить себя
- **WHEN** `DELETE /api/spaces/:space_id/members/:user_id` где `user_id` совпадает с авторизованным пользователем
- **THEN** сервер отвечает `400 Bad Request` с телом `{"error": "Cannot remove yourself"}`

### Requirement: REST API для настроек напоминаний

Система ДОЛЖНА предоставлять эндпоинты для управления настройками напоминаний пользователя.

#### Scenario: Получение текущих настроек
- **WHEN** `GET /api/user/reminders` от авторизованного пользователя
- **THEN** возвращается JSON с настройками: `{"1d": true, "2h": true, "1h": false, "30m": false, "15m": true, "0m": true}`

#### Scenario: Обновление настроек
- **WHEN** `PUT /api/user/reminders` с телом `{"1h": true, "30m": true}` от авторизованного пользователя
- **THEN** указанные настройки обновляются (merge, не replace), возвращаются полные настройки

### Requirement: Уведомления участников через бота при изменениях из API

При редактировании или удалении событий/пространств через API, система ДОЛЖНА отправлять уведомления участникам через Telegram бота, используя тот же формат что и текущие уведомления из бота.

#### Scenario: Уведомление при редактировании события через API
- **WHEN** владелец редактирует событие через `PUT /api/events/:id`
- **THEN** всем участникам пространства (кроме владельца) отправляется уведомление через Telegram бота с указанием что изменилось

#### Scenario: Уведомление при удалении события через API
- **WHEN** владелец удаляет событие через `DELETE /api/events/:id`
- **THEN** всем участникам пространства (кроме владельца) отправляется уведомление через Telegram бота

#### Scenario: Ошибка отправки уведомления не блокирует API
- **WHEN** уведомление не удаётся отправить одному из участников
- **THEN** ошибка логируется, API-запрос завершается успешно

### Requirement: REST API для языка пользователя

Mini App backend ДОЛЖЕН предоставлять эндпоинты для чтения и обновления языка:
- `GET /api/user/language` — возвращает `{"language": "<code>"}` (200)
- `PUT /api/user/language` — принимает `{"language": "<code>"}`, обновляет поле `language` пользователя, возвращает `{"language": "<code>"}` (200)

Валидация: `language` ДОЛЖЕН быть `"ru"` или `"en"`. При невалидном значении — 400 `{"error": "Invalid language. Supported: ru, en"}`.

#### Scenario: Получение текущего языка
- **WHEN** авторизованный пользователь отправляет `GET /api/user/language`
- **THEN** сервер возвращает 200 с `{"language": "ru"}` (или текущий язык пользователя)

#### Scenario: Смена языка на английский
- **WHEN** авторизованный пользователь отправляет `PUT /api/user/language` с телом `{"language": "en"}`
- **THEN** сервер обновляет `language` пользователя на `"en"` и возвращает 200 с `{"language": "en"}`

#### Scenario: Невалидный язык
- **WHEN** пользователь отправляет `PUT /api/user/language` с телом `{"language": "de"}`
- **THEN** сервер возвращает 400 с `{"error": "Invalid language. Supported: ru, en"}`

#### Scenario: Пользователь не найден
- **WHEN** пользователь с неизвестным ID отправляет `GET /api/user/language`
- **THEN** сервер возвращает 404 с `{"error": "User not found"}`

### Requirement: Обработка ошибок API

Все ошибки API ДОЛЖНЫ возвращаться в формате `{"error": "<описание>"}` с соответствующим HTTP-статусом.

#### Scenario: Валидационная ошибка
- **WHEN** клиент отправляет невалидные данные (пустой title, title > 500 символов)
- **THEN** сервер отвечает `400 Bad Request` с описанием ошибки

#### Scenario: Внутренняя ошибка
- **WHEN** происходит необработанное исключение
- **THEN** сервер отвечает `500 Internal Server Error`, детали логируются, клиент получает `{"error": "Internal server error"}`
