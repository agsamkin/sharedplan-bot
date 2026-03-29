# Capability: database-schema

## Purpose

Схема базы данных: 5 ORM-моделей (User, Space, UserSpace, Event, ScheduledReminder), async engine с asyncpg, начальная Alembic-миграция.

## Requirements

### Requirement: Async SQLAlchemy engine и session factory

Модуль `app/db/engine.py` ДОЛЖЕН создавать async engine через `create_async_engine` с драйвером `postgresql+asyncpg` и предоставлять `async_sessionmaker` для создания сессий.

#### Scenario: Создание engine из DATABASE_URL

- **WHEN** приложение стартует с валидным `DATABASE_URL`
- **THEN** создаётся async engine с подключением к PostgreSQL

### Requirement: ORM-модель User

Таблица `users` ДОЛЖНА содержать:
- `id` (BIGINT, PK — Telegram user ID)
- `username` (VARCHAR(255), NULLABLE)
- `first_name` (VARCHAR(255), NOT NULL)
- `reminder_settings` (JSONB, NOT NULL, DEFAULT `{"1d": true, "2h": true, "1h": false, "30m": false, "15m": true, "0m": true}`)
- `language` (VARCHAR(5), NOT NULL, DEFAULT `'en'`)
- `created_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW)

#### Scenario: Таблица users создаётся с правильной схемой

- **WHEN** Alembic применяет начальную миграцию
- **THEN** таблица `users` существует со всеми колонками, типами и ограничениями

#### Scenario: Новый пользователь с языком по умолчанию
- **WHEN** создаётся запись пользователя без указания языка
- **THEN** поле `language` содержит `'en'`

#### Scenario: Пользователь с явно указанным языком
- **WHEN** создаётся запись пользователя с `language = 'ru'`
- **THEN** поле `language` содержит `'ru'`

### Requirement: ORM-модель Space

Таблица `spaces` ДОЛЖНА содержать: `id` (UUID, PK, DEFAULT gen_random_uuid()), `name` (VARCHAR(255), NOT NULL), `invite_code` (VARCHAR(32), UNIQUE, NOT NULL), `created_by` (BIGINT, FK → users.id, NOT NULL), `created_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW).

#### Scenario: Таблица spaces создаётся с правильной схемой

- **WHEN** Alembic применяет начальную миграцию
- **THEN** таблица `spaces` существует с UNIQUE на `invite_code` и FK на `users.id`

### Requirement: ORM-модель UserSpace

Таблица `user_spaces` ДОЛЖНА содержать: `user_id` (BIGINT, FK → users.id ON DELETE CASCADE), `space_id` (UUID, FK → spaces.id ON DELETE CASCADE), `role` (VARCHAR(20), NOT NULL, CHECK IN ('admin', 'member')), `joined_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW). Составной PK на `(user_id, space_id)`.

#### Scenario: Таблица user_spaces создаётся с правильной схемой

- **WHEN** Alembic применяет начальную миграцию
- **THEN** таблица `user_spaces` существует с составным PK, ON DELETE CASCADE на обоих FK, CHECK-ограничением на `role`

### Requirement: ORM-модель Event

Таблица `events` ДОЛЖНА содержать: `id` (UUID, PK, DEFAULT gen_random_uuid()), `space_id` (UUID, FK → spaces.id ON DELETE CASCADE, NOT NULL), `title` (VARCHAR(500), NOT NULL), `event_date` (DATE, NOT NULL), `event_time` (TIME, NULLABLE), `created_by` (BIGINT, FK → users.id, NOT NULL), `raw_input` (TEXT, NULLABLE), `recurrence_rule` (VARCHAR 20, nullable — допустимые значения: daily, weekly, biweekly, monthly, yearly), `parent_event_id` (UUID, nullable, FK → events.id ON DELETE CASCADE), `created_at` (TIMESTAMPTZ, NOT NULL, DEFAULT NOW). Индексы: `idx_events_space_date` на `(space_id, event_date)`, `idx_events_parent` на `(parent_event_id)`.

#### Scenario: Таблица events создаётся с правильной схемой и индексом

- **WHEN** Alembic применяет начальную миграцию
- **THEN** таблица `events` существует со всеми колонками, FK с CASCADE на `spaces.id`, и индексом `idx_events_space_date`

#### Scenario: Одноразовое событие (обратная совместимость)
- **WHEN** создаётся одноразовое событие
- **THEN** `recurrence_rule = NULL` и `parent_event_id = NULL`

#### Scenario: Родительское повторяющееся событие
- **WHEN** создаётся повторяющееся событие
- **THEN** `recurrence_rule` содержит одно из допустимых значений, `parent_event_id = NULL`

#### Scenario: Дочернее вхождение
- **WHEN** генерируется вхождение повторяющегося события
- **THEN** `parent_event_id` указывает на родительское событие, `recurrence_rule = NULL`

#### Scenario: Каскадное удаление дочерних вхождений
- **WHEN** удаляется родительское событие
- **THEN** все дочерние вхождения (по `parent_event_id`) удаляются каскадно

### Requirement: ORM-модель ScheduledReminder

Таблица `scheduled_reminders` ДОЛЖНА содержать: `id` (UUID, PK, DEFAULT gen_random_uuid()), `event_id` (UUID, FK → events.id ON DELETE CASCADE, NOT NULL), `user_id` (BIGINT, FK → users.id ON DELETE CASCADE, NOT NULL), `remind_at` (TIMESTAMPTZ, NOT NULL), `reminder_type` (VARCHAR(10), NOT NULL), `sent` (BOOLEAN, NOT NULL, DEFAULT FALSE). Индекс `idx_reminders_remind_at_sent` на `(remind_at, sent)`.

#### Scenario: Таблица scheduled_reminders создаётся с правильной схемой и индексом

- **WHEN** Alembic применяет начальную миграцию
- **THEN** таблица `scheduled_reminders` существует со всеми колонками, FK с CASCADE, и индексом `idx_reminders_remind_at_sent`

### Requirement: Начальная Alembic миграция

Все 5 таблиц ДОЛЖНЫ создаваться в одной Alembic-миграции. Alembic ДОЛЖЕН быть сконфигурирован для async-работы с asyncpg.

#### Scenario: Alembic upgrade head создаёт все таблицы

- **WHEN** выполняется `alembic upgrade head` на пустой базе
- **THEN** создаются таблицы `users`, `spaces`, `user_spaces`, `events`, `scheduled_reminders` со всеми индексами и ограничениями

#### Scenario: Повторный upgrade head — идемпотентность

- **WHEN** выполняется `alembic upgrade head` на уже мигрированной базе
- **THEN** ничего не происходит, ошибок нет

### Requirement: Миграция для добавления поля language

Alembic-миграция ДОЛЖНА добавить колонку `language VARCHAR(5) NOT NULL DEFAULT 'en'` в таблицу `users`. Миграция ДОЛЖНА быть обратимой (downgrade удаляет колонку).

#### Scenario: Применение миграции
- **WHEN** выполняется `alembic upgrade head`
- **THEN** таблица `users` содержит колонку `language` с default `'en'`

#### Scenario: Откат миграции
- **WHEN** выполняется `alembic downgrade -1`
- **THEN** колонка `language` удаляется из таблицы `users`

### Requirement: Миграция recurring events

Alembic-миграция ДОЛЖНА добавить колонки `recurrence_rule` (VARCHAR 20, nullable) и `parent_event_id` (UUID, nullable, FK → events.id ON DELETE CASCADE) в таблицу `events`, а также индекс `idx_events_parent` на `parent_event_id`. Миграция ДОЛЖНА быть обратимой (downgrade удаляет колонки и индекс).

#### Scenario: Применение миграции
- **WHEN** выполняется `alembic upgrade head`
- **THEN** таблица events содержит колонки `recurrence_rule` и `parent_event_id` с индексом

#### Scenario: Откат миграции
- **WHEN** выполняется `alembic downgrade`
- **THEN** колонки `recurrence_rule`, `parent_event_id` и индекс `idx_events_parent` удаляются
