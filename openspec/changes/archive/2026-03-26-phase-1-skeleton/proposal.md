## Why

Проект Shared Plan Bot начинается с нуля. Чтобы все последующие фазы (пространства, события, AI-парсинг, напоминания) имели надёжный фундамент, необходим работающий скелет: структура проекта, Docker-окружение, база данных со всеми таблицами, конфигурация и минимальный Telegram-бот. Это первая фаза — без неё невозможна никакая дальнейшая работа.

## What Changes

- Создание структуры Python-проекта с модульной организацией (`app/bot/handlers/`, `app/bot/keyboards/`, `app/bot/callbacks/`, `app/bot/states/`, `app/bot/middlewares/`, `app/services/`, `app/db/`, `app/scheduler/`)
- Docker Compose стек: Python-бот (hot reload) + PostgreSQL 16 (persistent volume)
- Dockerfile на базе `python:3.12-slim`
- Конфигурация через `.env` + pydantic-settings с валидацией при старте
- SQLAlchemy 2.0 async ORM-модели всех 5 таблиц: `users`, `spaces`, `user_spaces`, `events`, `scheduled_reminders`
- Alembic async-миграции с начальной миграцией, создающей все таблицы
- aiogram 3.x приложение: Bot, Dispatcher, Router, long-polling
- Обработчик `/start` — приветствие + upsert пользователя в БД
- Обработчик `/help` — список команд
- Middleware для внедрения async DB-сессии в каждый handler
- `.env.example` и `requirements.txt` с зафиксированными версиями

## Capabilities

### New Capabilities

- `docker-environment`: Docker Compose стек (бот + PostgreSQL), Dockerfile, persistent volume, health checks, порядок запуска
- `app-config`: Конфигурация приложения через pydantic-settings: все env-переменные, валидация при старте, `.env.example`
- `database-schema`: SQLAlchemy ORM-модели всех таблиц, async engine, session factory, Alembic миграции
- `telegram-bot-core`: Базовое aiogram 3.x приложение: Bot, Dispatcher, Router, long-polling, обработчики `/start` и `/help`, upsert пользователя, middleware DB-сессии

### Modified Capabilities

Нет существующих capabilities — это первоначальная настройка проекта.

## Impact

- **Новые файлы**: вся структура `app/`, `alembic/`, `Dockerfile`, `docker-compose.yml`, `alembic.ini`, `requirements.txt`, `.env.example`
- **Зависимости**: aiogram 3.x, SQLAlchemy 2.0, asyncpg, alembic, pydantic-settings, APScheduler (установка, но использование в Фазе 6)
- **Внешние системы**: PostgreSQL 16 (Docker), Telegram Bot API (long-polling)
- **Инфраструктура**: Docker Compose как единственный способ запуска
