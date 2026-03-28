# Capability: space-management

## Purpose

Управление пространствами (spaces): сервисный слой (shared между ботом и Mini App API), вспомогательные фильтры. Команды /newspace, /spaces, /space_info и inline-клавиатура удалены — создание и просмотр пространств перенесены в Mini App. Управление участниками и удаление пространств также в Mini App.

## Requirements

### Requirement: Сервисный слой space_service.py

Вся бизнес-логика пространств ДОЛЖНА быть в `services/space_service.py` как async-функции, принимающие `session: AsyncSession`. Handlers бота и API-хендлеры Mini App НЕ ДОЛЖНЫ содержать прямых запросов к БД. Сервис ДОЛЖЕН использоваться как из бота (join flow в /start), так и из Mini App API (создание пространства).

#### Scenario: API-хендлер вызывает сервис для создания пространства
- **WHEN** API-хендлер обрабатывает POST /api/spaces
- **THEN** хендлер вызывает `space_service.create_space(session, user_id, name)`, который создаёт записи в `spaces` и `user_spaces` и возвращает созданное пространство с invite-кодом

#### Scenario: Handler /start вызывает сервис для join flow
- **WHEN** handler обрабатывает /start с deep link join_*
- **THEN** handler вызывает `space_service.join_space(session, user_id, invite_code)` для присоединения к пространству

### Requirement: Фильтр not_command

Модуль `filters/not_command.py` ДОЛЖЕН предоставлять фильтр, определяющий, что текстовое сообщение не является командой бота (не начинается с `/`).

#### Scenario: Обычное текстовое сообщение проходит фильтр

- **WHEN** пользователь отправляет сообщение "Привет"
- **THEN** фильтр `not_command` возвращает True

#### Scenario: Команда не проходит фильтр

- **WHEN** пользователь отправляет сообщение `/start`
- **THEN** фильтр `not_command` возвращает False
