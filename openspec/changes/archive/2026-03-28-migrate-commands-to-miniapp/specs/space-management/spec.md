## REMOVED Requirements

### Requirement: Создание пространства через /newspace с FSM
**Reason**: Создание пространств перенесено в Mini App. Команда /newspace и FSM CreateSpace больше не нужны.
**Migration**: Пользователи создают пространства через экран spaceCreate в Mini App (POST /api/spaces).

### Requirement: Список пространств через /spaces
**Reason**: Список пространств доступен в Mini App на главном экране. Команда /spaces дублирует функциональность.
**Migration**: Пользователи просматривают пространства в Mini App (GET /api/spaces).

### Requirement: Информация о пространстве через /space_info
**Reason**: Информация о пространстве доступна в Mini App на экране spaceDetail. Команда /space_info дублирует функциональность.
**Migration**: Пользователи просматривают информацию в Mini App (GET /api/spaces/:id).

### Requirement: Inline-клавиатура выбора пространства
**Reason**: Inline-клавиатура использовалась для выбора пространства в командах /events, /space_info. Эти команды удалены.
**Migration**: Выбор пространства реализован в Mini App как навигация по списку.

## MODIFIED Requirements

### Requirement: Сервисный слой space_service.py

Вся бизнес-логика пространств ДОЛЖНА быть в `services/space_service.py` как async-функции, принимающие `session: AsyncSession`. Handlers бота и API-хендлеры Mini App НЕ ДОЛЖНЫ содержать прямых запросов к БД. Сервис ДОЛЖЕН использоваться как из бота (join flow в /start), так и из Mini App API (создание пространства).

#### Scenario: API-хендлер вызывает сервис для создания пространства
- **WHEN** API-хендлер обрабатывает POST /api/spaces
- **THEN** хендлер вызывает `space_service.create_space(session, user_id, name)`, который создаёт записи в `spaces` и `user_spaces` и возвращает созданное пространство с invite-кодом

#### Scenario: Handler /start вызывает сервис для join flow
- **WHEN** handler обрабатывает /start с deep link join_*
- **THEN** handler вызывает `space_service.join_space(session, user_id, invite_code)` для присоединения к пространству
