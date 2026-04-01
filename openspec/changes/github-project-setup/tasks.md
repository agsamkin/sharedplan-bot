## 1. Конфигурация БД — раздельные переменные

- [x] 1.1 Обновить `app/config.py`: добавить `DB_USER`, `DB_PASSWORD`, `DB_HOST` (default `localhost`), `DB_PORT` (default `5432`), `DB_NAME` (default `sharedplan`), сделать `DATABASE_URL` опциональным, добавить `model_validator` для сборки `DATABASE_URL` из компонентов
- [x] 1.2 Обновить `.env.example`: добавить раздельные переменные БД с комментариями, сохранить `DATABASE_URL` как альтернативу
- [x] 1.3 Обновить `docker-compose.yml`: заменить хардкод `POSTGRES_USER: postgres` / `POSTGRES_PASSWORD: postgres` / `POSTGRES_DB: sharedplan` на `${DB_USER:-postgres}` / `${DB_PASSWORD:-postgres}` / `${DB_NAME:-sharedplan}`, обновить `pg_isready -U` на `${DB_USER:-postgres}`

## 2. Лицензия

- [x] 2.1 Создать файл `LICENSE` в корне с текстом MIT License (год 2024-2026, copyright holder из git config или generic)

## 3. README.md

- [x] 3.1 Создать `README.md`: заголовок, описание проекта, пометка «демо-проект, создан с помощью AI (Claude Opus 4.6, OpenSpec)»
- [x] 3.2 Добавить секцию «Возможности» — список ключевых фич (spaces, события, напоминания, Mini App, AI-парсинг, голосовой ввод)
- [x] 3.3 Добавить секцию «Quick Start» — клонирование, копирование `.env.example`, заполнение переменных, `docker compose up`
- [x] 3.4 Добавить таблицу переменных окружения — имя, обязательность, default, описание
- [x] 3.5 Добавить секции «Разработка», «Тесты», «Лицензия»

## 4. GitHub Actions CI

- [x] 4.1 Создать `.github/workflows/ci.yml`: trigger на push/PR в main, job с PostgreSQL 16 service container
- [x] 4.2 Добавить шаги: checkout, setup Python 3.12, install requirements + requirements-dev, pytest --cov
- [x] 4.3 Добавить шаг сборки Docker-образа (`docker build .`)
- [x] 4.4 Добавить upload coverage artifact

## 5. Верификация

- [x] 5.1 Убедиться что `python -c "from app.config import settings"` работает с раздельными переменными БД
- [x] 5.2 Убедиться что `docker compose config` валиден с новыми переменными
- [x] 5.3 Запустить `pytest` — все существующие тесты проходят
