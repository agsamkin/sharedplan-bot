## ADDED Requirements

### Requirement: Middleware обновления профиля пользователя

Middleware `UserProfileMiddleware` ДОЛЖЕН при каждом входящем сообщении или callback обновлять `first_name` и `username` пользователя в таблице `users`. Middleware ДОЛЖЕН регистрироваться после `DbSessionMiddleware`.

#### Scenario: first_name изменился в Telegram
- **WHEN** пользователь с id=123 отправляет сообщение, и его текущий `first_name` в Telegram отличается от записи в БД
- **THEN** поле `first_name` обновляется в таблице `users`

#### Scenario: Новый пользователь (не в БД)
- **WHEN** пользователь, отсутствующий в БД, отправляет любое сообщение
- **THEN** создаётся запись в `users` с текущими `first_name`, `username` и дефолтными `reminder_settings`

#### Scenario: username стал NULL
- **WHEN** пользователь удалил свой Telegram username
- **THEN** поле `username` обновляется на NULL в таблице `users`

### Requirement: Логирование пользовательских команд

Каждая обработанная команда бота ДОЛЖНА логироваться с информацией: command, user_id. Для команд, связанных с пространством — дополнительно space_id.

#### Scenario: Команда /spaces
- **WHEN** пользователь с id=123 отправляет `/spaces`
- **THEN** в лог записывается: `"/spaces user_id=123"`

#### Scenario: Команда /events с выбором пространства
- **WHEN** пользователь с id=123 запрашивает `/events` и выбирает пространство с id=abc-123
- **THEN** в лог записывается: `"/events user_id=123 space_id=abc-123"`

#### Scenario: Текстовое сообщение (создание события)
- **WHEN** пользователь с id=123 отправляет текст для создания события
- **THEN** в лог записывается: `"event_create user_id=123"`

## MODIFIED Requirements

### Requirement: Точка входа в main.py

Модуль `app/main.py` ДОЛЖЕН быть точкой входа: создание Bot, Dispatcher, подключение роутеров и middleware, запуск Alembic миграций, запуск long-polling. ДОЛЖНЫ быть зарегистрированы роутеры обработчиков событий (`event.py`, `events_list.py`) и callback-обработчиков (`event_confirm.py`). Перед запуском polling ДОЛЖНЫ выполняться startup-проверки: PostgreSQL connectivity и Telegram token validation.

#### Scenario: Запуск приложения
- **WHEN** выполняется `python -m app.main`
- **THEN** проверяется связность с PostgreSQL, применяются миграции, проверяется Telegram-токен, регистрируются все роутеры и middleware (включая UserProfileMiddleware), запускается APScheduler, запускается long-polling

#### Scenario: Роутер событий зарегистрирован
- **WHEN** бот запущен
- **THEN** текстовые сообщения (не команды) маршрутизируются к обработчику событий в `handlers/event.py`

#### Scenario: Роутер списка событий зарегистрирован
- **WHEN** бот запущен
- **THEN** команда `/events` маршрутизируется к обработчику в `handlers/events_list.py`
