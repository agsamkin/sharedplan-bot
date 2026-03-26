## ADDED Requirements

### Requirement: Docker Compose стек запускает бот и PostgreSQL

Система ДОЛЖНА разворачиваться одной командой `docker compose up`, запуская два сервиса: `bot` (Python-приложение) и `db` (PostgreSQL 16).

#### Scenario: Успешный запуск стека

- **WHEN** пользователь выполняет `docker compose up`
- **THEN** запускаются сервисы `bot` и `db`, бот подключается к PostgreSQL и начинает long-polling

#### Scenario: PostgreSQL стартует раньше бота

- **WHEN** Docker Compose запускает сервисы
- **THEN** сервис `bot` запускается только после того, как `db` пройдёт health check через `pg_isready`

### Requirement: Dockerfile на базе Python 3.12-slim

Сервис `bot` ДОЛЖЕН собираться из Dockerfile на базе образа `python:3.12-slim` с установкой зависимостей из `requirements.txt`.

#### Scenario: Сборка Docker-образа бота

- **WHEN** выполняется `docker compose build` или `docker compose up --build`
- **THEN** создаётся образ на базе `python:3.12-slim` с установленными зависимостями

### Requirement: Персистентность данных PostgreSQL

Данные PostgreSQL ДОЛЖНЫ сохраняться между перезапусками контейнеров через именованный Docker volume `postgres_data`.

#### Scenario: Данные сохраняются после перезапуска

- **WHEN** выполняется `docker compose down` и затем `docker compose up`
- **THEN** все данные в PostgreSQL сохранены (таблицы, записи)

#### Scenario: Полная очистка данных

- **WHEN** выполняется `docker compose down -v`
- **THEN** volume `postgres_data` удаляется и данные теряются

### Requirement: Порядок запуска при старте бота

При запуске сервиса `bot` ДОЛЖНА соблюдаться последовательность: Alembic миграции → aiogram long-polling. Если миграция или подключение к БД завершается ошибкой, процесс ДОЛЖЕН завершиться с ненулевым кодом.

#### Scenario: Успешный старт с миграциями

- **WHEN** сервис `bot` запускается и PostgreSQL доступен
- **THEN** Alembic применяет все ожидающие миграции, затем aiogram начинает long-polling

#### Scenario: Ошибка подключения к БД

- **WHEN** сервис `bot` запускается, но PostgreSQL недоступен
- **THEN** процесс завершается с ненулевым кодом и сообщением об ошибке
