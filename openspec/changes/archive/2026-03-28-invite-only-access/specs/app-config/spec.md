## MODIFIED Requirements

### Requirement: Обязательные переменные окружения

Система ДОЛЖНА требовать следующие переменные: `TELEGRAM_BOT_TOKEN`, `DATABASE_URL` (формат `postgresql+asyncpg://...`), `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `NEXARA_API_KEY`, `OWNER_TELEGRAM_ID` (Telegram user ID владельца бота, целое число).

#### Scenario: Все обязательные переменные заданы

- **WHEN** в `.env` указаны все 6 обязательных переменных (включая `OWNER_TELEGRAM_ID`)
- **THEN** приложение успешно стартует

#### Scenario: Отсутствие OWNER_TELEGRAM_ID

- **WHEN** переменная `OWNER_TELEGRAM_ID` отсутствует
- **THEN** приложение завершается с ошибкой при старте и описательным сообщением

### Requirement: Файл .env.example

В корне проекта ДОЛЖЕН существовать файл `.env.example` со всеми переменными окружения и комментариями, описывающими назначение каждой.

#### Scenario: .env.example содержит все переменные

- **WHEN** разработчик открывает `.env.example`
- **THEN** файл содержит все 8 переменных (6 обязательных + 2 опциональных) с комментариями, включая `OWNER_TELEGRAM_ID` с описанием «Telegram ID владельца бота (число)»
