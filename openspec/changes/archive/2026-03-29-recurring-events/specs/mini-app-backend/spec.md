## MODIFIED Requirements

### Requirement: POST /api/spaces/:space_id/events
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

### Requirement: GET /api/spaces/:space_id/events
Возвращает `{"events": [...], "total_count": N}`. Будущие события, сортировка по дате ASC / времени ASC NULLS FIRST. Лимит по умолчанию 50, максимум 100. Каждое событие включает `id`, `title`, `event_date`, `event_time`, `created_by`, `creator_name`, `is_owner`, **`recurrence_rule`**, **`parent_event_id`**. Дочерние вхождения (`parent_event_id != null`) НЕ возвращаются в списке — только родительские события и одноразовые.

#### Scenario: Список событий с повторяющимися
- **WHEN** GET запрос списка событий пространства
- **THEN** возвращаются только родительские и одноразовые события (без дочерних вхождений), каждое с полем `recurrence_rule`

### Requirement: GET /api/events/:event_id
Возвращает детали события с `space_id`, `space_name`, `is_owner`, `created_at`, **`recurrence_rule`**, **`parent_event_id`**.

#### Scenario: Детали повторяющегося события
- **WHEN** GET запрос к повторяющемуся событию
- **THEN** ответ содержит `recurrence_rule: "weekly"` (или другое значение)

### Requirement: PUT /api/events/:event_id
Обновление события (title/date/time/**recurrence_rule**). Только владелец (403 если нет). При изменении date/time — пересоздать неотправленные напоминания. При изменении `recurrence_rule` — удалить все будущие дочерние вхождения и сгенерировать новые по новому правилу (или удалить все если `recurrence_rule` стал null). Уведомить участников. Возвращает обновлённое событие с `recurrence_rule`.

#### Scenario: Изменение правила повторения
- **WHEN** PUT с `{"recurrence_rule": "monthly"}` для события с текущим `recurrence_rule: "weekly"`
- **THEN** будущие дочерние вхождения пересоздаются по правилу `monthly`, возвращается обновлённое событие

#### Scenario: Отключение повторения
- **WHEN** PUT с `{"recurrence_rule": null}` для повторяющегося события
- **THEN** все дочерние вхождения удаляются, событие становится одноразовым

### Requirement: DELETE /api/events/:event_id
Удаление события с каскадным удалением напоминаний и дочерних вхождений (через FK ON DELETE CASCADE). Только владелец (403 если нет). Уведомить участников. Вернуть 204.

#### Scenario: Удаление повторяющегося события
- **WHEN** DELETE запрос к повторяющемуся событию
- **THEN** удаляется родительское событие, все дочерние вхождения и их напоминания каскадно, возвращается 204
