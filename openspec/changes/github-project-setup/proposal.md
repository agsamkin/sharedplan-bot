## Why

Проект готов функционально, но не оформлен для публикации на GitHub. Нет README, лицензии, .env.example не содержит переменных БД (логин/пароль/хост/порт отдельно), отсутствует CI/CD. Для публичного репозитория необходимы: документация для запуска, явная лицензия, CI-пайплайн и пометка о демо-характере проекта.

## What Changes

- Создать `README.md` с описанием проекта, инструкциями по запуску, списком переменных окружения (обязательные и опциональные), пометкой что это демо-проект, реализованный с помощью AI (Claude Opus 4.6, OpenSpec)
- Обновить `.env.example` — вынести переменные БД раздельно: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` (сейчас только монолитный `DATABASE_URL`)
- Обновить `app/config.py` — добавить раздельные переменные БД и автосборку `DATABASE_URL`
- Обновить `docker-compose.yml` — использовать новые переменные вместо хардкода `postgres:postgres`
- Создать файл `LICENSE` (MIT — максимально permissive, разрешает форки и модификации)
- Создать `.github/workflows/ci.yml` — GitHub Actions: сборка Docker-образа, запуск тестов, отчёт покрытия

## Capabilities

### New Capabilities
- `github-readme`: README.md с описанием, quick start, переменными окружения, демо-пометкой
- `github-ci`: GitHub Actions workflow — сборка, тесты, покрытие кода

### Modified Capabilities
- `app-config`: добавление раздельных переменных БД (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`) с автосборкой `DATABASE_URL`
- `docker-environment`: использование новых env-переменных вместо хардкода credentials

## Impact

- **Файлы:** README.md (новый), LICENSE (новый), .github/workflows/ci.yml (новый), .env.example (обновление), app/config.py (обновление), docker-compose.yml (обновление)
- **Обратная совместимость:** `DATABASE_URL` остаётся рабочим — если задан напрямую, используется как есть; раздельные переменные — альтернатива
- **CI:** новый workflow не влияет на существующий процесс разработки
