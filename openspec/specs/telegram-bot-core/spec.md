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

Команда `/help` ДОЛЖНА отправлять краткую справку по работе с ботом. Справка ДОЛЖНА содержать: инструкцию по созданию событий (текст/голосовое сообщение), описание Mini App для управления (через кнопку меню), список команд: `/help`, `/privacy`.

#### Scenario: Пользователь отправляет /help
- **WHEN** пользователь отправляет `/help`
- **THEN** бот отвечает сообщением со справкой по работе с ботом и ссылкой на Mini App

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

Middleware `UserProfileMiddleware` обновляет `first_name` и `username` пользователя при каждом входящем сообщении или callback. Регистрируется после `DbSessionMiddleware`. При upsert нового пользователя middleware ДОЛЖЕН определить язык из `language_code` Telegram: если `language_code` начинается с `"ru"` — устанавливает `language = "ru"`, иначе — `language = "en"`. Для существующих пользователей `language` НЕ ДОЛЖЕН перезаписываться. После upsert middleware ДОЛЖЕН передать `data["lang"]` со значением `language` пользователя из БД.

#### Scenario: first_name изменился в Telegram
- **WHEN** пользователь с id=123 отправляет сообщение, и его текущий `first_name` в Telegram отличается от записи в БД
- **THEN** поле `first_name` обновляется в таблице `users`

#### Scenario: Новый пользователь (не в БД)
- **WHEN** пользователь, отсутствующий в БД, отправляет любое сообщение
- **THEN** создаётся запись в `users` с текущими `first_name`, `username` и дефолтными `reminder_settings`

#### Scenario: username стал NULL
- **WHEN** пользователь удалил свой Telegram username
- **THEN** поле `username` обновляется на NULL в таблице `users`

#### Scenario: Новый пользователь с русским Telegram
- **WHEN** пользователь с `language_code = "ru-RU"` впервые взаимодействует с ботом
- **THEN** создаётся запись с `language = "ru"`, `data["lang"] = "ru"`

#### Scenario: Новый пользователь с английским Telegram
- **WHEN** пользователь с `language_code = "en"` впервые взаимодействует с ботом
- **THEN** создаётся запись с `language = "en"`, `data["lang"] = "en"`

#### Scenario: Новый пользователь с неизвестным языком
- **WHEN** пользователь с `language_code = "de"` впервые взаимодействует с ботом
- **THEN** создаётся запись с `language = "en"`, `data["lang"] = "en"`

#### Scenario: Существующий пользователь — язык не перезаписывается
- **WHEN** существующий пользователь с `language = "ru"` отправляет сообщение, а его `language_code` в Telegram сменился на `"en"`
- **THEN** поле `language` в БД остаётся `"ru"`, `data["lang"] = "ru"`

#### Scenario: first_name изменился
- **WHEN** пользователь с изменённым `first_name` отправляет сообщение
- **THEN** `first_name` обновляется, `language` не затрагивается

#### Scenario: username стал NULL (при смене языка не затрагивается)
- **WHEN** пользователь удалил username в Telegram
- **THEN** `username` обновляется на NULL, `language` не затрагивается

### Requirement: Логирование пользовательских команд

Каждая обработанная команда бота ДОЛЖНА логироваться с информацией: command, user_id. Логируемые команды: `/start`, `/help`, `/privacy`.

#### Scenario: Команда /privacy
- **WHEN** пользователь с id=123 отправляет `/privacy`
- **THEN** в лог записывается: `"/privacy user_id=123"`

#### Scenario: Текстовое сообщение (создание события)
- **WHEN** пользователь с id=123 отправляет текст для создания события
- **THEN** в лог записывается: `"event_create user_id=123"`

### Requirement: Запуск aiohttp web server в main.py

Модуль `app/main.py` ДОЛЖЕН запускать aiohttp web server одновременно с aiogram long-polling в одном asyncio event loop. Web server ДОЛЖЕН получать экземпляр `Bot` для отправки уведомлений из API-хендлеров.

#### Scenario: Запуск приложения с web server
- **WHEN** выполняется `python -m app.main`
- **THEN** проверяется связность с PostgreSQL, применяются миграции, проверяется Telegram-токен, регистрируются роутеры и middleware, запускается APScheduler, запускается aiohttp web server на `MINI_APP_PORT`, запускается aiogram long-polling

#### Scenario: Web server получает Bot instance
- **WHEN** aiohttp web server инициализируется
- **THEN** экземпляр `Bot` доступен в `app` context для использования в API-хендлерах (отправка уведомлений)

### Requirement: Конфигурация Mini App

Модуль `app/config.py` ДОЛЖЕН содержать настройки Mini App: `MINI_APP_URL` (URL для WebApp-кнопок), `MINI_APP_PORT` (порт web server, default `8080`).

#### Scenario: Настройки Mini App из env
- **WHEN** приложение загружает конфигурацию
- **THEN** `MINI_APP_URL` и `MINI_APP_PORT` читаются из переменных окружения

### Requirement: Точка входа в main.py

Модуль `app/main.py` ДОЛЖЕН быть точкой входа: создание Bot, Dispatcher, подключение роутеров и middleware, запуск Alembic миграций, запуск aiohttp web server, запуск long-polling. ДОЛЖНЫ быть зарегистрированы роутеры: `start.router`, `help.router`, `privacy.router`, `event_confirm_cb.router`, `space_select_cb.router`, `voice.router`, `event.router`. Роутеры `space.router`, `events_list.router`, `reminders.router`, `mini_app.router` ДОЛЖНЫ быть удалены. При наличии `MINI_APP_URL` ДОЛЖНА устанавливаться `MenuButtonWebApp` через `set_chat_menu_button()`. Перед запуском polling ДОЛЖНЫ выполняться startup-проверки.

#### Scenario: Запуск приложения
- **WHEN** выполняется `python -m app.main`
- **THEN** проверяется связность с PostgreSQL, применяются миграции, проверяется Telegram-токен, регистрируются роутеры (start, help, privacy, event_confirm_cb, space_select_cb, voice, event) и middleware (включая UserProfileMiddleware), устанавливается MenuButtonWebApp, запускается APScheduler, запускается aiohttp web server, запускается long-polling

#### Scenario: Удалённые роутеры не регистрируются
- **WHEN** бот запущен
- **THEN** роутеры space, events_list, reminders и mini_app НЕ зарегистрированы

### Requirement: Зависимости в requirements.txt

Файл `requirements.txt` ДОЛЖЕН содержать все зависимости проекта с зафиксированными версиями: aiogram, SQLAlchemy, asyncpg, alembic, pydantic-settings, apscheduler, openai, aiohttp. Зависимость aiohttp уже присутствует и используется для web server.

#### Scenario: Установка зависимостей
- **WHEN** выполняется `pip install -r requirements.txt`
- **THEN** все необходимые пакеты устанавливаются с точными версиями
