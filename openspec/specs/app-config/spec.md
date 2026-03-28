# Capability: app-config

## Purpose

Конфигурация приложения через pydantic-settings: загрузка и валидация переменных окружения, обязательные и опциональные параметры, файл-шаблон `.env.example`.

## Requirements

### Requirement: Конфигурация через pydantic-settings

Модуль `app/config.py` ДОЛЖЕН использовать `pydantic-settings` для загрузки и валидации переменных окружения из файла `.env`.

#### Scenario: Успешная загрузка конфигурации

- **WHEN** все обязательные переменные окружения заданы
- **THEN** объект `Settings` создаётся с типизированными значениями

#### Scenario: Отсутствие обязательной переменной

- **WHEN** отсутствует одна из обязательных переменных (`TELEGRAM_BOT_TOKEN`, `DATABASE_URL`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `NEXARA_API_KEY`)
- **THEN** приложение завершается с ошибкой при старте и описательным сообщением

### Requirement: Обязательные переменные окружения

Система ДОЛЖНА требовать следующие переменные: `TELEGRAM_BOT_TOKEN`, `DATABASE_URL` (формат `postgresql+asyncpg://...`), `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `NEXARA_API_KEY`, `OWNER_TELEGRAM_ID` (Telegram user ID владельца бота, целое число).

#### Scenario: Все обязательные переменные заданы

- **WHEN** в `.env` указаны все 6 обязательных переменных (включая `OWNER_TELEGRAM_ID`)
- **THEN** приложение успешно стартует

#### Scenario: Отсутствие OWNER_TELEGRAM_ID

- **WHEN** переменная `OWNER_TELEGRAM_ID` отсутствует
- **THEN** приложение завершается с ошибкой при старте и описательным сообщением

### Requirement: Опциональные переменные с дефолтными значениями

Система ДОЛЖНА поддерживать опциональные переменные: `TIMEZONE` (по умолчанию `Europe/Moscow`), `REMINDER_CHECK_INTERVAL_SECONDS` (по умолчанию `30`).

#### Scenario: Опциональные переменные не заданы

- **WHEN** переменные `TIMEZONE` и `REMINDER_CHECK_INTERVAL_SECONDS` отсутствуют
- **THEN** используются значения по умолчанию: `Europe/Moscow` и `30`

#### Scenario: Опциональные переменные заданы

- **WHEN** `TIMEZONE=Europe/Berlin` и `REMINDER_CHECK_INTERVAL_SECONDS=60` заданы
- **THEN** используются указанные значения

### Requirement: Файл .env.example

В корне проекта ДОЛЖЕН существовать файл `.env.example` со всеми переменными окружения и комментариями, описывающими назначение каждой.

#### Scenario: .env.example содержит все переменные

- **WHEN** разработчик открывает `.env.example`
- **THEN** файл содержит все 8 переменных (6 обязательных + 2 опциональных) с комментариями, включая `OWNER_TELEGRAM_ID` с описанием «Telegram ID владельца бота (число)»
