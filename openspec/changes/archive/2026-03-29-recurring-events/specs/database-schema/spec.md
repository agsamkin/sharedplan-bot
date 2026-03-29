## MODIFIED Requirements

### Requirement: Event model
Таблица `events` c колонками: `id` (UUID, PK, server_default uuid4), `space_id` (UUID, FK → spaces.id ON DELETE CASCADE, NOT NULL), `title` (VARCHAR 500, NOT NULL), `event_date` (DATE, NOT NULL), `event_time` (TIME, nullable), `created_by` (BIGINT, FK → users.id, NOT NULL), `raw_input` (TEXT, nullable), `recurrence_rule` (VARCHAR 20, nullable — допустимые значения: daily, weekly, biweekly, monthly, yearly), `parent_event_id` (UUID, nullable, FK → events.id ON DELETE CASCADE), `created_at` (TIMESTAMPTZ, server_default now()). Индексы: `idx_events_space_date` на (space_id, event_date), `idx_events_parent` на (parent_event_id).

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

## ADDED Requirements

### Requirement: Миграция recurring events
Alembic-миграция ДОЛЖНА добавить колонки `recurrence_rule` (VARCHAR 20, nullable) и `parent_event_id` (UUID, nullable, FK → events.id ON DELETE CASCADE) в таблицу `events`, а также индекс `idx_events_parent` на `parent_event_id`. Миграция ДОЛЖНА быть обратимой (downgrade удаляет колонки и индекс).

#### Scenario: Применение миграции
- **WHEN** выполняется `alembic upgrade head`
- **THEN** таблица events содержит колонки `recurrence_rule` и `parent_event_id` с индексом

#### Scenario: Откат миграции
- **WHEN** выполняется `alembic downgrade`
- **THEN** колонки `recurrence_rule`, `parent_event_id` и индекс `idx_events_parent` удаляются
