# Shared Plan Bot

Telegram-бот для совместного планирования событий в небольших группах. Пользователи создают spaces (общие календари), добавляют события текстом или голосом, получают персонализированные напоминания. Включает Telegram Mini App для управления через веб-интерфейс.

> **Демо-проект.** Этот проект создан с использованием AI — [Claude Opus 4.6](https://claude.ai/) и [OpenSpec](https://github.com/Fission-AI/OpenSpec).

## Возможности

- **Spaces** — общие календари для групп. Создание, приглашения по ссылке, управление участниками
- **События** — создание событий текстом с AI-парсингом даты/времени через LLM (OpenRouter)
- **Голосовой ввод** — распознавание голосовых сообщений через Nexara STT и автоматическое создание событий
- **Напоминания** — персональные настройки (за 1 день, 2 часа, 1 час, 30 мин, 15 мин, в момент события)
- **Повторяющиеся события** — ежедневные, еженедельные, ежемесячные, ежегодные
- **Mini App** — React SPA внутри Telegram для удобного управления событиями и пространствами

## Quick Start

```bash
# 1. Клонировать репозиторий
git clone https://github.com/<your-username>/sharedplan.git
cd sharedplan

# 2. Настроить переменные окружения
cp .env.example .env
# Отредактировать .env — заполнить TELEGRAM_BOT_TOKEN и OWNER_TELEGRAM_ID

# 3. Запустить
docker compose up
```

Бот автоматически применит миграции БД, запустит планировщик напоминаний и Mini App web server.

> **Доступ:** после запуска бот доступен только его владельцу (`OWNER_TELEGRAM_ID`). Другие пользователи могут получить доступ, присоединившись по пригласительной ссылке от владельца.

## Переменные окружения

| Переменная | Обязательна | По умолчанию | Описание |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | да | — | Токен бота от @BotFather |
| `OWNER_TELEGRAM_ID` | да | — | Telegram ID владельца бота |
| `DATABASE_URL` | нет* | — | Полный connection string (`postgresql+asyncpg://...`) |
| `DB_USER` | нет* | — | Имя пользователя PostgreSQL |
| `DB_PASSWORD` | нет* | — | Пароль PostgreSQL |
| `DB_HOST` | нет | `localhost` | Хост PostgreSQL |
| `DB_PORT` | нет | `5432` | Порт PostgreSQL |
| `DB_NAME` | нет | `sharedplan` | Имя базы данных |
| `OPENROUTER_API_KEY` | нет | — | API-ключ OpenRouter для AI-парсинга событий |
| `OPENROUTER_MODEL` | нет | — | Модель OpenRouter (напр. `openai/gpt-4o-mini`) |
| `NEXARA_API_KEY` | нет | — | API-ключ Nexara для голосового ввода |
| `TIMEZONE` | нет | `Europe/Moscow` | Часовой пояс |
| `REMINDER_CHECK_INTERVAL_SECONDS` | нет | `30` | Интервал проверки напоминаний (сек) |
| `MINI_APP_URL` | нет | — | URL Mini App для WebApp-кнопок |
| `MINI_APP_PORT` | нет | `8080` | Порт Mini App web server |

\* Необходимо задать либо `DATABASE_URL`, либо `DB_USER` + `DB_PASSWORD`.

## Разработка

```bash
# Запуск без Docker (при наличии PostgreSQL)
pip install -r requirements.txt
python -m app.main

# Миграции
alembic upgrade head
alembic revision --autogenerate -m "description"

# Mini App frontend
cd mini_app/frontend
npm install
npm run dev       # dev-сервер
npm run build     # production-сборка
```

## Тесты

```bash
pip install -r requirements-dev.txt

pytest                          # все тесты
pytest tests/test_auth.py       # конкретный файл
pytest --cov                    # с покрытием
pytest --cov --cov-report=html  # HTML-отчёт в htmlcov/
```

## Стек технологий

- **Python 3.12+**, aiogram 3.x, SQLAlchemy 2.0 async, asyncpg, APScheduler
- **PostgreSQL 16**
- **React 18** + TypeScript + Vite (Mini App)
- **Docker Compose** для развёртывания

## Лицензия

[MIT](LICENSE)
