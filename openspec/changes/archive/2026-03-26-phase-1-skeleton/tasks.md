## 1. Конфигурация и зависимости

- [x] 1.1 Создать `requirements.txt` с зафиксированными версиями: aiogram, SQLAlchemy, asyncpg, alembic, pydantic-settings, apscheduler, openai, aiohttp
- [x] 1.2 Создать `app/config.py` — pydantic-settings класс `Settings` с 5 обязательными и 2 опциональными переменными
- [x] 1.3 Создать `.env.example` со всеми переменными и комментариями

## 2. Docker-окружение

- [x] 2.1 Создать `Dockerfile` на базе `python:3.12-slim` с установкой зависимостей и точкой входа `python -m app.main`
- [x] 2.2 Создать `docker-compose.yml` с сервисами `bot` и `db` (postgres:16-alpine), health check через `pg_isready`, depends_on с condition, volume `postgres_data`

## 3. База данных — engine и модели

- [x] 3.1 Создать структуру каталогов `app/` со всеми `__init__.py` (`app/`, `app/bot/`, `app/bot/handlers/`, `app/bot/keyboards/`, `app/bot/callbacks/`, `app/bot/states/`, `app/bot/middlewares/`, `app/services/`, `app/db/`, `app/scheduler/`)
- [x] 3.2 Создать `app/db/engine.py` — async engine через `create_async_engine`, `async_sessionmaker`
- [x] 3.3 Создать `app/db/models.py` — ORM-модели всех 5 таблиц: `User`, `Space`, `UserSpace`, `Event`, `ScheduledReminder` с типами, FK, CASCADE, CHECK, индексами, дефолтами

## 4. Alembic миграции

- [x] 4.1 Создать `alembic.ini` и `alembic/env.py` с async-конфигурацией (asyncpg, импорт моделей)
- [x] 4.2 Создать начальную миграцию `alembic/versions/001_initial_schema.py` — все 5 таблиц в одной транзакции

## 5. Telegram-бот — ядро

- [x] 5.1 Создать `app/bot/middlewares/db_session.py` — middleware для внедрения async DB-сессии, commit при успехе, rollback при ошибке
- [x] 5.2 Создать `app/bot/handlers/start.py` — обработчик `/start`: приветствие + upsert пользователя (INSERT ON CONFLICT DO UPDATE first_name, username)
- [x] 5.3 Создать `app/bot/handlers/help.py` — обработчик `/help`: список команд бота
- [x] 5.4 Создать `app/main.py` — точка входа: создание Bot/Dispatcher, подключение роутеров и middleware, запуск Alembic миграций при старте, запуск long-polling
