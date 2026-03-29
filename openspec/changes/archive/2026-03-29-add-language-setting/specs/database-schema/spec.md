## MODIFIED Requirements

### Requirement: ORM-модель User
Таблица `users` ДОЛЖНА содержать:
- `id` (BIGINT, PK — Telegram user ID)
- `username` (VARCHAR(255), NULLABLE)
- `first_name` (VARCHAR(255), NOT NULL)
- `reminder_settings` (JSONB, NOT NULL, DEFAULT `{"1d": true, "2h": true, "1h": false, "30m": false, "15m": true, "0m": true}`)
- `language` (VARCHAR(5), NOT NULL, DEFAULT `'en'`)
- `created_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW)

#### Scenario: Новый пользователь с языком по умолчанию
- **WHEN** создаётся запись пользователя без указания языка
- **THEN** поле `language` содержит `'en'`

#### Scenario: Пользователь с явно указанным языком
- **WHEN** создаётся запись пользователя с `language = 'ru'`
- **THEN** поле `language` содержит `'ru'`

## ADDED Requirements

### Requirement: Миграция для добавления поля language
Alembic-миграция ДОЛЖНА добавить колонку `language VARCHAR(5) NOT NULL DEFAULT 'en'` в таблицу `users`. Миграция ДОЛЖНА быть обратимой (downgrade удаляет колонку).

#### Scenario: Применение миграции
- **WHEN** выполняется `alembic upgrade head`
- **THEN** таблица `users` содержит колонку `language` с default `'en'`

#### Scenario: Откат миграции
- **WHEN** выполняется `alembic downgrade -1`
- **THEN** колонка `language` удаляется из таблицы `users`
