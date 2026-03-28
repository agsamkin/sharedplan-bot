## ADDED Requirements

### Requirement: Сборка фронтенда Mini App в Docker

Dockerfile ДОЛЖЕН включать multi-stage build: первый этап собирает фронтенд (Node.js + npm), второй — финальный образ с Python и собранным фронтендом.

#### Scenario: Multi-stage сборка
- **WHEN** выполняется `docker compose build`
- **THEN** первый этап устанавливает Node.js зависимости и собирает React SPA через `npm run build`, второй этап копирует `dist/` в финальный Python-образ

#### Scenario: Фронтенд доступен в контейнере
- **WHEN** контейнер `bot` запущен
- **THEN** собранные файлы фронтенда доступны по пути `/app/mini_app/frontend/dist/` внутри контейнера

### Requirement: Порт Mini App в Docker Compose

Docker Compose ДОЛЖЕН пробрасывать порт `MINI_APP_PORT` (default `8080`) из контейнера `bot` на хост.

#### Scenario: Порт Mini App доступен
- **WHEN** Docker Compose стек запущен
- **THEN** aiohttp web server доступен на `http://localhost:8080` (или настроенном порте)

## MODIFIED Requirements

### Requirement: Docker Compose стек запускает бот и PostgreSQL

Система ДОЛЖНА разворачиваться одной командой `docker compose up`, запуская два сервиса: `bot` (Python-приложение с Telegram ботом и web server для Mini App) и `db` (PostgreSQL 16).

#### Scenario: Успешный запуск стека
- **WHEN** пользователь выполняет `docker compose up`
- **THEN** запускаются сервисы `bot` и `db`, бот подключается к PostgreSQL, начинает long-polling и запускает web server для Mini App

#### Scenario: PostgreSQL стартует раньше бота
- **WHEN** Docker Compose запускает сервисы
- **THEN** сервис `bot` запускается только после того, как `db` пройдёт health check через `pg_isready`

### Requirement: Dockerfile на базе Python 3.12-slim

Сервис `bot` ДОЛЖЕН собираться из multi-stage Dockerfile: первый этап — `node:20-slim` для сборки фронтенда, второй — `python:3.12-slim` для бота с копированием собранного фронтенда.

#### Scenario: Сборка Docker-образа бота
- **WHEN** выполняется `docker compose build` или `docker compose up --build`
- **THEN** создаётся multi-stage образ: Node.js собирает фронтенд, Python 3.12-slim — финальный образ с ботом и статикой
