## MODIFIED Requirements

### Requirement: Обработчик /help

Команда `/help` ДОЛЖНА отправлять краткую справку по работе с ботом. Справка ДОЛЖНА содержать: инструкцию по созданию событий (текст/голосовое сообщение), описание Mini App для управления (через кнопку меню), список команд: `/help`, `/privacy`.

#### Scenario: Пользователь отправляет /help
- **WHEN** пользователь отправляет `/help`
- **THEN** бот отвечает сообщением со справкой по работе с ботом и ссылкой на Mini App

### Requirement: Точка входа в main.py

Модуль `app/main.py` ДОЛЖЕН быть точкой входа: создание Bot, Dispatcher, подключение роутеров и middleware, запуск Alembic миграций, запуск aiohttp web server, запуск long-polling. ДОЛЖНЫ быть зарегистрированы роутеры: `start.router`, `help.router`, `privacy.router`, `event_confirm_cb.router`, `space_select_cb.router`, `voice.router`, `event.router`. Роутеры `space.router`, `events_list.router`, `reminders.router`, `mini_app.router` ДОЛЖНЫ быть удалены. При наличии `MINI_APP_URL` ДОЛЖНА устанавливаться `MenuButtonWebApp` через `set_chat_menu_button()`. Перед запуском polling ДОЛЖНЫ выполняться startup-проверки.

#### Scenario: Запуск приложения
- **WHEN** выполняется `python -m app.main`
- **THEN** проверяется связность с PostgreSQL, применяются миграции, проверяется Telegram-токен, регистрируются роутеры (start, help, privacy, event_confirm_cb, space_select_cb, voice, event) и middleware (включая UserProfileMiddleware), устанавливается MenuButtonWebApp, запускается APScheduler, запускается aiohttp web server, запускается long-polling

#### Scenario: Удалённые роутеры не регистрируются
- **WHEN** бот запущен
- **THEN** роутеры space, events_list, reminders и mini_app НЕ зарегистрированы

### Requirement: Логирование пользовательских команд

Каждая обработанная команда бота ДОЛЖНА логироваться с информацией: command, user_id. Логируемые команды: `/start`, `/help`, `/privacy`.

#### Scenario: Команда /privacy
- **WHEN** пользователь с id=123 отправляет `/privacy`
- **THEN** в лог записывается: `"/privacy user_id=123"`

#### Scenario: Текстовое сообщение (создание события)
- **WHEN** пользователь с id=123 отправляет текст для создания события
- **THEN** в лог записывается: `"event_create user_id=123"`
