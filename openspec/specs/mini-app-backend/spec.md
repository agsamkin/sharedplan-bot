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
- **THEN** возвращается JSON-массив будущих событий, отсортированных по `event_date ASC, event_time ASC NULLS FIRST`, с полями: `id`, `title`, `event_date`, `event_time`, `created_by`, `creator_name`, `is_owner`

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

### Requirement: Обработка ошибок API

Все ошибки API ДОЛЖНЫ возвращаться в формате `{"error": "<описание>"}` с соответствующим HTTP-статусом.

#### Scenario: Валидационная ошибка
- **WHEN** клиент отправляет невалидные данные (пустой title, title > 500 символов)
- **THEN** сервер отвечает `400 Bad Request` с описанием ошибки

#### Scenario: Внутренняя ошибка
- **WHEN** происходит необработанное исключение
- **THEN** сервер отвечает `500 Internal Server Error`, детали логируются, клиент получает `{"error": "Internal server error"}`
