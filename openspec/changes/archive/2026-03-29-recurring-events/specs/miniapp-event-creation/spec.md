## MODIFIED Requirements

### Requirement: Form fields
Форма создания события ДОЛЖНА содержать: Title (текстовое поле, placeholder, autofocus), Date (обязательное), Time (обязательное), **Repeat** (RepeatPicker — выпадающий селектор с опциями: "Не повторять", "Каждый день", "Каждую неделю", "Каждые 2 недели", "Каждый месяц", "Каждый год"; значение по умолчанию — "Не повторять"). Дизайн RepeatPicker ДОЛЖЕН соответствовать макету из `docs/shared-plan-miniapp.jsx`.

#### Scenario: Отображение RepeatPicker
- **WHEN** пользователь открывает форму создания события
- **THEN** под полем времени отображается RepeatPicker со значением "Не повторять" по умолчанию

#### Scenario: Выбор повторения
- **WHEN** пользователь нажимает на RepeatPicker и выбирает "Каждую неделю"
- **THEN** RepeatPicker показывает "Каждую неделю" с фиолетовой подсветкой и иконкой повторения

### Requirement: Submission
`POST /api/spaces/:space_id/events` с телом `{"title", "event_date", "event_time", "recurrence_rule"}`. Значение `recurrence_rule` — строка (`daily`, `weekly`, `biweekly`, `monthly`, `yearly`) или `null` если "Не повторять". При успехе: навигация назад + toast "Событие создано". При ошибке: toast с текстом ошибки.

#### Scenario: Создание повторяющегося события
- **WHEN** пользователь заполняет форму с повторением "Каждый месяц" и нажимает "Создать событие"
- **THEN** отправляется POST с `recurrence_rule: "monthly"`, при успехе показывается toast

#### Scenario: Создание одноразового события
- **WHEN** пользователь оставляет "Не повторять" и нажимает "Создать событие"
- **THEN** отправляется POST с `recurrence_rule: null`
