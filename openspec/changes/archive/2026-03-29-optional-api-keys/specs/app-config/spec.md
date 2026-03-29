## MODIFIED Requirements

### Requirement: Обязательные переменные окружения

Система ДОЛЖНА требовать следующие переменные: `TELEGRAM_BOT_TOKEN`, `DATABASE_URL` (формат `postgresql+asyncpg://...`), `OWNER_TELEGRAM_ID` (Telegram user ID владельца бота, целое число).

Переменные `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `NEXARA_API_KEY` ДОЛЖНЫ быть опциональными (`Optional[str]` с default `None`).

#### Scenario: Все обязательные переменные заданы, API-ключи отсутствуют

- **WHEN** в `.env` указаны `TELEGRAM_BOT_TOKEN`, `DATABASE_URL`, `OWNER_TELEGRAM_ID`, но отсутствуют `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `NEXARA_API_KEY`
- **THEN** приложение успешно стартует с ограниченной функциональностью

#### Scenario: Все переменные заданы включая API-ключи

- **WHEN** в `.env` указаны все переменные включая `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `NEXARA_API_KEY`
- **THEN** приложение стартует с полной функциональностью

#### Scenario: Отсутствие OWNER_TELEGRAM_ID

- **WHEN** переменная `OWNER_TELEGRAM_ID` отсутствует
- **THEN** приложение завершается с ошибкой при старте и описательным сообщением

### Requirement: Файл .env.example

В корне проекта ДОЛЖЕН существовать файл `.env.example` со всеми переменными окружения и комментариями, описывающими назначение каждой. Опциональные API-ключи ДОЛЖНЫ быть помечены комментарием «(опционально)».

#### Scenario: .env.example содержит все переменные

- **WHEN** разработчик открывает `.env.example`
- **THEN** файл содержит все переменные: 3 обязательных (`TELEGRAM_BOT_TOKEN`, `DATABASE_URL`, `OWNER_TELEGRAM_ID`), 3 опциональных API-ключа (`OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `NEXARA_API_KEY`) с пометкой «(опционально)», и 2 опциональных с дефолтами (`TIMEZONE`, `REMINDER_CHECK_INTERVAL_SECONDS`)
