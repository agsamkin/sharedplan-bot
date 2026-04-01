## MODIFIED Requirements

### Requirement: Docker Compose стек запускает бот и PostgreSQL

Система ДОЛЖНА разворачиваться одной командой `docker compose up`, запуская два сервиса: `bot` (Python-приложение с Telegram ботом и web server для Mini App) и `db` (PostgreSQL 16).

Сервис `db` ДОЛЖЕН использовать переменные окружения `DB_USER`, `DB_PASSWORD`, `DB_NAME` из `.env` файла вместо хардкода credentials. При отсутствии этих переменных ДОЛЖНЫ использоваться значения по умолчанию: `postgres`, `postgres`, `sharedplan`.

#### Scenario: Успешный запуск стека
- **WHEN** пользователь выполняет `docker compose up`
- **THEN** запускаются сервисы `bot` и `db`, бот подключается к PostgreSQL, начинает long-polling и запускает web server для Mini App

#### Scenario: PostgreSQL стартует раньше бота
- **WHEN** Docker Compose запускает сервисы
- **THEN** сервис `bot` запускается только после того, как `db` пройдёт health check через `pg_isready`

#### Scenario: Кастомные credentials БД
- **WHEN** в `.env` заданы `DB_USER=myuser`, `DB_PASSWORD=mypass`, `DB_NAME=mydb`
- **THEN** PostgreSQL создаётся с указанными credentials и бот подключается используя их
