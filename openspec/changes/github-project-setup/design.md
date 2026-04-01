## Context

Проект Shared Plan Bot функционально готов, но не имеет документации, лицензии и CI/CD для публикации на GitHub. Текущее состояние:
- `.env.example` содержит монолитный `DATABASE_URL`, credentials БД захардкожены в `docker-compose.yml`
- Нет README.md, LICENSE, GitHub Actions workflow
- `app/config.py` использует единый `DATABASE_URL` без возможности задать компоненты раздельно

## Goals / Non-Goals

**Goals:**
- README.md с описанием проекта, инструкциями запуска, перечнем переменных окружения и пометкой «демо-проект, создан с помощью AI»
- Раздельные env-переменные для БД (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`) с обратной совместимостью через `DATABASE_URL`
- Файл лицензии MIT
- GitHub Actions CI: сборка, тесты (`pytest`), отчёт покрытия

**Non-Goals:**
- CD (деплой) — только CI
- Публикация Docker-образа в registry
- Миграция существующих `.env` файлов
- Badges в README (можно добавить позже)

## Decisions

### 1. Обратная совместимость DATABASE_URL

**Решение:** `DATABASE_URL` остаётся приоритетным. Если задан — используется как есть. Если не задан — собирается из `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` через `model_validator`.

**Альтернатива:** Полностью убрать `DATABASE_URL` в пользу раздельных переменных. Отвергнуто — ломает существующие деплои.

### 2. Лицензия MIT

**Решение:** MIT — максимально permissive, разрешает любое использование, форки, модификации. Соответствует требованию пользователя.

**Альтернатива:** Apache 2.0 (больше защиты патентов) или Unlicense (public domain). MIT — самый распространённый и понятный выбор.

### 3. GitHub Actions CI — PostgreSQL service container

**Решение:** CI workflow использует `services.postgres` в GitHub Actions для запуска реальной PostgreSQL рядом с тестами. Шаги: checkout → setup Python → install deps → run pytest с coverage → upload coverage artifact.

**Альтернатива:** Docker Compose в CI. Отвергнуто — медленнее, сложнее (нужен build контейнера), service container проще и стандартнее для GitHub Actions.

### 4. Структура README

**Решение:** Секции: описание → демо-пометка → возможности → quick start (Docker Compose) → переменные окружения (таблица) → разработка → тесты → лицензия.

## Risks / Trade-offs

- **[Раздельные DB-переменные усложняют конфиг]** → Митигация: `DATABASE_URL` остаётся основным способом; раздельные переменные — альтернатива для удобства Docker Compose. Валидатор проверяет что задан хотя бы один из вариантов.
- **[CI тесты могут падать на чужих форках]** → Митигация: CI не использует секреты (TELEGRAM_BOT_TOKEN и т.д. не нужны для тестов). PostgreSQL поднимается как service container.
