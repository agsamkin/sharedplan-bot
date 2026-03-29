## MODIFIED Requirements

### Requirement: Space detail screen
Экран деталей пространства (`/spaces/:id`) ДОЛЖЕН отображать список будущих событий с: названием, датой (относительный формат), временем (если есть), **информацией о повторении** (если есть), автором. Формат подзаголовка события: `{relative_date} · {time} · {repeat_label} · {author}` — пропускать отсутствующие части. Повторение отображается текстом из i18n `repeatOptions` (например "Каждую неделю"). Дочерние вхождения (`parent_event_id != null`) НЕ отображаются отдельно — показывается только родительское событие с меткой повторения.

#### Scenario: Отображение повторяющегося события в списке
- **WHEN** в пространстве есть повторяющееся событие с `recurrence_rule = "weekly"`
- **THEN** в списке событий подзаголовок содержит "Каждую неделю"

#### Scenario: Отображение одноразового события
- **WHEN** событие имеет `recurrence_rule = null`
- **THEN** подзаголовок НЕ содержит информации о повторении

### Requirement: Event editing screen
Экран редактирования события (`/events/:id`) ДОЛЖЕН содержать: title, date picker, time picker, **RepeatPicker** (компонент из макета `docs/shared-plan-miniapp.jsx`). RepeatPicker отображает текущее значение `recurrence_rule` и позволяет изменить его. При сохранении отправляется `PUT /api/events/:id` с полем `recurrence_rule`.

#### Scenario: Редактирование повторения
- **WHEN** пользователь открывает редактирование события с `recurrence_rule = "monthly"`
- **THEN** RepeatPicker показывает "Каждый месяц" как текущее значение

#### Scenario: Сохранение изменения повторения
- **WHEN** пользователь меняет повторение на "Каждую неделю" и нажимает "Сохранить"
- **THEN** отправляется PUT с `recurrence_rule: "weekly"`

### Requirement: i18n integration
Все строки ДОЛЖНЫ быть доступны через `useTranslation()`. Словари ДОЛЖНЫ включать: `repeat` ("Повтор" / "Repeat"), `repeatOptions` (объект с ключами `none`, `daily`, `weekly`, `biweekly`, `monthly`, `yearly` и локализованными значениями для ru и en). Значения из макета: ru: none="Не повторять", daily="Каждый день", weekly="Каждую неделю", biweekly="Каждые 2 недели", monthly="Каждый месяц", yearly="Каждый год"; en: none="Never", daily="Every day", weekly="Every week", biweekly="Every 2 weeks", monthly="Every month", yearly="Every year".

#### Scenario: Локализация повторений на русском
- **WHEN** язык интерфейса русский и событие имеет `recurrence_rule = "biweekly"`
- **THEN** отображается "Каждые 2 недели"

#### Scenario: Локализация повторений на английском
- **WHEN** язык интерфейса английский и событие имеет `recurrence_rule = "biweekly"`
- **THEN** отображается "Every 2 weeks"

### Requirement: Event deletion dialog for recurring
Диалог удаления повторяющегося события ДОЛЖЕН отображать текст "Удалить «{title}» и все будущие повторения? Это действие нельзя отменить." вместо стандартного текста для одноразовых событий.

#### Scenario: Диалог удаления повторяющегося события
- **WHEN** пользователь нажимает "Удалить" для события с `recurrence_rule != null`
- **THEN** текст диалога предупреждает об удалении всех повторений
