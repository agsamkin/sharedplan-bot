# Capability: telegram-bot-core

## Purpose

Ядро Telegram-бота: aiogram 3.x приложение с long-polling, обработчики /start и /help, middleware для DB-сессий, точка входа main.py, зависимости.

## Requirements

### Requirement: aiogram 3.x приложение с long-polling

Приложение ДОЛЖНО использовать aiogram 3.x с Bot, Dispatcher и Router. Бот ДОЛЖЕН работать в режиме long-polling (не webhooks).

#### Scenario: Бот запускается в long-polling режиме

- **WHEN** приложение стартует через `python -m app.main`
- **THEN** aiogram начинает long-polling к Telegram Bot API и обрабатывает входящие обновления

### Requirement: Обработчик /start с upsert пользователя

Команда `/start` ДОЛЖНА отправлять приветственное сообщение и создавать (или обновлять) запись пользователя в таблице `users` по Telegram user ID. При обновлении ДОЛЖНЫ обновляться `first_name` и `username`.

При наличии deep link payload с префиксом `join_` обработчик ДОЛЖЕН перенаправлять на флоу присоединения к пространству вместо отображения приветствия. Upsert пользователя ДОЛЖЕН выполняться в обоих случаях.

#### Scenario: Новый пользователь отправляет /start

- **WHEN** пользователь, отсутствующий в БД, отправляет `/start` без payload
- **THEN** создаётся запись в `users` с Telegram ID, first_name, username и дефолтными `reminder_settings`, и отправляется приветственное сообщение

#### Scenario: Существующий пользователь отправляет /start

- **WHEN** пользователь, уже существующий в БД, отправляет `/start` без payload
- **THEN** обновляются `first_name` и `username` в записи `users`, и отправляется приветственное сообщение

#### Scenario: Пользователь без username отправляет /start

- **WHEN** пользователь без Telegram username отправляет `/start`
- **THEN** создаётся/обновляется запись с `username = NULL`

#### Scenario: /start с deep link join payload

- **WHEN** пользователь отправляет `/start join_abc12345`
- **THEN** выполняется upsert пользователя и запускается флоу присоединения к пространству по invite_code "abc12345"

#### Scenario: /start с невалидным deep link payload

- **WHEN** пользователь отправляет `/start` с payload, не начинающимся на `join_`
- **THEN** выполняется стандартное приветствие (payload игнорируется)

### Requirement: Обработчик /help

Команда `/help` ДОЛЖНА отправлять список доступных команд бота.

#### Scenario: Пользователь отправляет /help

- **WHEN** пользователь отправляет `/help`
- **THEN** бот отвечает сообщением со списком команд: `/start`, `/help`, `/newspace`, `/spaces`, `/space_info`, `/events`, `/reminders`

### Requirement: Middleware для DB-сессии

Middleware `db_session.py` ДОЛЖЕН создавать async-сессию SQLAlchemy для каждого входящего обновления, внедрять её в handler, коммитить при успехе и откатывать при исключении.

#### Scenario: Handler получает DB-сессию

- **WHEN** handler обрабатывает входящее сообщение
- **THEN** handler имеет доступ к async-сессии SQLAlchemy через аргументы

#### Scenario: Успешная обработка — сессия коммитится

- **WHEN** handler завершается без исключений
- **THEN** сессия коммитится и изменения сохраняются в БД

#### Scenario: Ошибка в handler — сессия откатывается

- **WHEN** handler бросает исключение
- **THEN** сессия откатывается, изменения не сохраняются

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

### Requirement: Зависимости в requirements.txt

Файл `requirements.txt` ДОЛЖЕН содержать все зависимости проекта с зафиксированными версиями: aiogram, SQLAlchemy, asyncpg, alembic, pydantic-settings, apscheduler, openai, aiohttp.

#### Scenario: Установка зависимостей

- **WHEN** выполняется `pip install -r requirements.txt`
- **THEN** все необходимые пакеты устанавливаются с точными версиями
