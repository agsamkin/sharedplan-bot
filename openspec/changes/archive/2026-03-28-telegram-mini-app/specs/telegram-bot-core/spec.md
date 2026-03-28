## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Точка входа в main.py

Модуль `app/main.py` ДОЛЖЕН быть точкой входа: создание Bot, Dispatcher, подключение роутеров и middleware, запуск Alembic миграций, запуск aiohttp web server, запуск long-polling. ДОЛЖНЫ быть зарегистрированы роутеры обработчиков событий (`event.py`, `events_list.py`) и callback-обработчиков (`event_confirm.py`). Перед запуском polling ДОЛЖНЫ выполняться startup-проверки: PostgreSQL connectivity и Telegram token validation.

#### Scenario: Запуск приложения
- **WHEN** выполняется `python -m app.main`
- **THEN** проверяется связность с PostgreSQL, применяются миграции, проверяется Telegram-токен, регистрируются все роутеры и middleware (включая UserProfileMiddleware), запускается APScheduler, запускается aiohttp web server, запускается long-polling

#### Scenario: Роутер событий зарегистрирован
- **WHEN** бот запущен
- **THEN** текстовые сообщения (не команды) маршрутизируются к обработчику событий в `handlers/event.py`

#### Scenario: Роутер списка событий зарегистрирован
- **WHEN** бот запущен
- **THEN** команда `/events` маршрутизируется к обработчику в `handlers/events_list.py`

### Requirement: Зависимости в requirements.txt

Файл `requirements.txt` ДОЛЖЕН содержать все зависимости проекта с зафиксированными версиями: aiogram, SQLAlchemy, asyncpg, alembic, pydantic-settings, apscheduler, openai, aiohttp. Зависимость aiohttp уже присутствует и используется для web server.

#### Scenario: Установка зависимостей
- **WHEN** выполняется `pip install -r requirements.txt`
- **THEN** все необходимые пакеты устанавливаются с точными версиями
