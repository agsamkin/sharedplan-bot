# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Shared Plan Bot — Telegram-бот для совместного планирования событий в небольших группах. Пользователи создают spaces (общие календари), добавляют события текстом или голосом (AI-парсинг через OpenRouter, STT через Nexara), получают персонализированные напоминания. Включает Telegram Mini App (React SPA) для управления через веб-интерфейс.

## Tech Stack

**Бот (Python):**
- **Python 3.12+**, async-first (asyncio event loop)
- **aiogram 3.x** — Telegram Bot API, long-polling mode
- **SQLAlchemy 2.0 async + asyncpg** — ORM и доступ к PostgreSQL 16
- **Alembic** — миграции БД (async-конфигурация)
- **APScheduler** (AsyncIOScheduler) — фоновая задача проверки напоминаний
- **OpenRouter API** — LLM-парсинг текста в структурированные события (через `openai` SDK с кастомным `base_url`)
- **Nexara API** — speech-to-text для голосовых сообщений (через `aiohttp`)
- **aiohttp** — HTTP-сервер для Mini App backend
- **pydantic-settings** — конфигурация из `.env`

**Mini App (Frontend):**
- **React 18** + **TypeScript 5.6** — SPA
- **React Router DOM 7** — клиентская маршрутизация
- **Telegram WebApp SDK** (`@telegram-apps/sdk-react`) — интеграция с Telegram
- **Vite 6** — сборка

**Инфраструктура:** Docker Compose (бот + PostgreSQL 16)

## Build & Run

```bash
docker compose up          # запуск всего стека (bot + postgres)
docker compose up --build  # пересборка образа (multi-stage: frontend → Python)
```

При старте (`app/main.py`): проверка PostgreSQL → Alembic миграции → валидация Telegram-токена → APScheduler → aiohttp Mini App сервер → aiogram long-polling.

## Development Commands

```bash
# Миграции
alembic upgrade head              # применить все миграции
alembic revision --autogenerate -m "description"  # создать миграцию

# Тесты
pip install -r requirements-dev.txt  # установка dev-зависимостей (pytest, pytest-cov)
pytest                               # все тесты
pytest tests/test_auth.py            # конкретный файл
pytest tests/test_auth.py::test_name -v  # конкретный тест
pytest --cov                         # тесты с отчётом покрытия
pytest --cov --cov-report=html       # тесты + HTML-отчёт в htmlcov/

# Mini App frontend (из mini_app/frontend/)
npm install                       # установка зависимостей
npm run dev                       # dev-сервер (Vite)
npm run build                     # production-сборка → dist/

# Локальный запуск бота (без Docker, при наличии PostgreSQL)
python -m app.main
```

## Architecture

Однопроцессная async-архитектура. Бот, Mini App backend и scheduler работают в одном asyncio event loop, одном Docker-контейнере.

### Layer Rules

- **Handlers** (`app/bot/handlers/`) — Telegram-специфичная логика (форматирование, клавиатуры, FSM-переходы). Зависят от services. Не содержат бизнес-логики и прямых запросов к БД.
- **Callbacks** (`app/bot/callbacks/`) — обработчики inline-кнопок (подтверждение событий, выбор пространства).
- **Middlewares** (`app/bot/middlewares/`) — инъекция сессии БД, автосоздание профиля, контроль доступа.
- **Services** (`app/services/`) — бизнес-логика (создание событий, расчёт напоминаний, управление пространствами). Тестируемы без Telegram. Зависят от db/models.
- **Prompts** (`app/prompts/`) — динамическая генерация промптов для LLM-парсинга (few-shot примеры на основе текущей даты).
- **db/models** (`app/db/models.py`) — чистый data layer. Никакой логики, никаких импортов из приложения.
- **Клиенты API** (`llm_parser.py`, `speech_to_text.py`) — изолированные сервисы, можно замокать независимо.

### Mini App

- **Backend** (`mini_app/backend/`) — aiohttp-сервер со стеком middleware (error → auth → db_session). Три группы роутов: events, spaces, user.
- **Frontend** (`mini_app/frontend/src/`) — React SPA. Страницы в `pages/`, переиспользуемые компоненты в `components/`, API-клиент в `api/`.
- **Аутентификация** — валидация Telegram initData (HMAC-SHA256) в `mini_app/backend/auth.py`.
- **Сборка** — Dockerfile stage 1 (node) собирает frontend, stage 2 (python) копирует `dist/` и запускает бот.

### Key Design Decisions

- **Telegram user ID как PK** таблицы `users` (BIGINT, не синтетический UUID)
- **event_date (DATE) + event_time (TIME nullable)** — раздельные колонки, а не TIMESTAMPTZ, для корректной обработки событий без времени
- **Предвычисленные напоминания** — записи `scheduled_reminders` создаются при публикации события, планировщик просто делает `WHERE sent = FALSE AND remind_at <= NOW()`
- **reminder_settings как JSONB** в таблице users — 6 булевых флагов (`1d`, `2h`, `1h`, `30m`, `15m`, `0m`), читать через `.get(key, False)` для forward-compatibility
- **Единый часовой пояс `Europe/Moscow`** для всех операций
- **Mini App в одном процессе с ботом** — aiohttp-сервер запускается в том же event loop, не отдельный контейнер

### Callback Data Convention

Inline-кнопки используют формат `{action}:{entity_id}:{payload}` (напр. `event_confirm:{uuid}`, `reminder_toggle:1d`).

### Error Isolation

Сбой одной операции не каскадирует: каждая отправка уведомления/напоминания обёрнута в try/except. Неудачные напоминания помечаются `sent=TRUE` (нет бесконечных повторов).

## Configuration

Через `.env` + pydantic-settings.

**Обязательные:** `TELEGRAM_BOT_TOKEN`, `DATABASE_URL` (async: `postgresql+asyncpg://...`), `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `NEXARA_API_KEY`, `OWNER_TELEGRAM_ID`.

**Опциональные:** `TIMEZONE` (default `Europe/Moscow`), `REMINDER_CHECK_INTERVAL_SECONDS` (default `30`), `MINI_APP_URL`, `MINI_APP_PORT` (default `8080`).

## Language

Все артефакты проекта — OpenSpec-спеки, описания изменений, комментарии в коде, commit-сообщения, документация — создаются на **русском языке**.

## OpenSpec Workflow

Проект использует OpenSpec для управления изменениями. Спеки хранятся в `openspec/specs/` (24 спеки), текущие изменения в `openspec/changes/`, архив завершённых — в `openspec/changes/archive/`. Используйте `/opsx:*` команды для работы с изменениями. Все спеки и артефакты OpenSpec пишутся на русском.
