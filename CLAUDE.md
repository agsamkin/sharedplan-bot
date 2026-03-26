# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Shared Plan Bot — Telegram-бот для совместного планирования событий в небольших группах. Пользователи создают spaces (общие календари), добавляют события текстом или голосом (AI-парсинг через OpenRouter, STT через Nexara), получают персонализированные напоминания.

## Tech Stack

- **Python 3.12+**, async-first (asyncio event loop)
- **aiogram 3.x** — Telegram Bot API, long-polling mode
- **SQLAlchemy 2.0 async + asyncpg** — ORM и доступ к PostgreSQL 16
- **Alembic** — миграции БД (async-конфигурация)
- **APScheduler** (AsyncIOScheduler) — фоновая задача проверки напоминаний
- **OpenRouter API** — LLM-парсинг текста в структурированные события (через `openai` SDK с кастомным `base_url`)
- **Nexara API** — speech-to-text для голосовых сообщений (через `aiohttp`)
- **pydantic-settings** — конфигурация из `.env`
- **Docker Compose** — бот + PostgreSQL

## Build & Run

```bash
docker compose up          # запуск всего стека
docker compose up --build  # пересборка образа бота
```

При старте: PostgreSQL → Alembic миграции → APScheduler → aiogram long-polling.

## Development Commands

```bash
# Миграции
alembic upgrade head              # применить все миграции
alembic revision --autogenerate -m "description"  # создать миграцию

# Локальный запуск (без Docker, при наличии PostgreSQL)
python -m app.main
```

## Architecture

Однопроцессная async-архитектура. Все компоненты работают в одном asyncio event loop.

### Layer Rules

- **Handlers** (`app/bot/handlers/`) — Telegram-специфичная логика (форматирование, клавиатуры, FSM-переходы). Зависят от services. Не содержат бизнес-логики и прямых запросов к БД.
- **Services** (`app/services/`) — бизнес-логика (создание событий, расчёт напоминаний, управление пространствами). Тестируемы без Telegram. Зависят от db/models.
- **db/models** (`app/db/models.py`) — чистый data layer. Никакой логики, никаких импортов из приложения.
- **Клиенты API** (`llm_parser.py`, `speech_to_text.py`) — изолированные сервисы, можно замокать независимо.

### Key Design Decisions

- **Telegram user ID как PK** таблицы `users` (BIGINT, не синтетический UUID)
- **event_date (DATE) + event_time (TIME nullable)** — раздельные колонки, а не TIMESTAMPTZ, для корректной обработки событий без времени
- **Предвычисленные напоминания** — записи `scheduled_reminders` создаются при публикации события, планировщик просто делает `WHERE sent = FALSE AND remind_at <= NOW()`
- **reminder_settings как JSONB** в таблице users — 6 булевых флагов, читать через `.get(key, False)` для forward-compatibility
- **Единый часовой пояс `Europe/Moscow`** для всех операций

### Callback Data Convention

Inline-кнопки используют формат `{action}:{entity_id}:{payload}` (напр. `event_confirm:{uuid}`, `reminder_toggle:1d`).

### Error Isolation

Сбой одной операции не каскадирует: каждая отправка уведомления/напоминания обёрнута в try/except. Неудачные напоминания помечаются `sent=TRUE` (нет бесконечных повторов).

## Configuration

Через `.env` + pydantic-settings. Обязательные: `TELEGRAM_BOT_TOKEN`, `DATABASE_URL` (async: `postgresql+asyncpg://...`), `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `NEXARA_API_KEY`. Опциональные: `TIMEZONE` (default `Europe/Moscow`), `REMINDER_CHECK_INTERVAL_SECONDS` (default `30`).

## Development Phases

Проект реализуется в 8 фазах (от ядра к периферии), описанных в `docs/phases.md`. Фазы 4-5 (AI) и 6 (напоминания) можно делать параллельно после Фазы 3.

## Language

Все артефакты проекта — OpenSpec-спеки, описания изменений, комментарии в коде, commit-сообщения, документация — создаются на **русском языке**.

## OpenSpec Workflow

Проект использует OpenSpec для управления изменениями. Спеки хранятся в `openspec/specs/`, текущие изменения в `openspec/changes/`. Используйте `/opsx:*` команды для работы с изменениями. Все спеки и артефакты OpenSpec пишутся на русском.
