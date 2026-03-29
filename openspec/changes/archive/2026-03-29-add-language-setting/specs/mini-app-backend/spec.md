## ADDED Requirements

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
