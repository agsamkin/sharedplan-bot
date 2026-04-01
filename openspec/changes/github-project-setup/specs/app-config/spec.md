## MODIFIED Requirements

### Requirement: Обязательные переменные окружения

Система ДОЛЖНА требовать следующие переменные: `TELEGRAM_BOT_TOKEN`, `OWNER_TELEGRAM_ID` (Telegram user ID владельца бота, целое число).

Переменная `DATABASE_URL` (формат `postgresql+asyncpg://...`) ДОЛЖНА быть опциональной. Если `DATABASE_URL` не задан, система ДОЛЖНА собирать его из раздельных переменных: `DB_USER`, `DB_PASSWORD`, `DB_HOST` (default `localhost`), `DB_PORT` (default `5432`), `DB_NAME` (default `sharedplan`). Если не задан ни `DATABASE_URL`, ни `DB_USER` + `DB_PASSWORD`, приложение ДОЛЖНО завершиться с ошибкой.

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

#### Scenario: DATABASE_URL не задан, раздельные переменные заданы
- **WHEN** `DATABASE_URL` отсутствует, но заданы `DB_USER=myuser`, `DB_PASSWORD=mypass`, `DB_HOST=db`, `DB_PORT=5432`, `DB_NAME=sharedplan`
- **THEN** система собирает `DATABASE_URL=postgresql+asyncpg://myuser:mypass@db:5432/sharedplan` и успешно подключается

#### Scenario: Ни DATABASE_URL, ни раздельные переменные не заданы
- **WHEN** `DATABASE_URL` отсутствует и `DB_USER` или `DB_PASSWORD` не задан
- **THEN** приложение завершается с ошибкой валидации при старте

### Requirement: Файл .env.example

В корне проекта ДОЛЖЕН существовать файл `.env.example` со всеми переменными окружения и комментариями, описывающими назначение каждой. Опциональные API-ключи ДОЛЖНЫ быть помечены комментарием «(опционально)». Файл ДОЛЖЕН содержать раздельные переменные БД (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`) как альтернативу `DATABASE_URL`.

#### Scenario: .env.example содержит все переменные
- **WHEN** разработчик открывает `.env.example`
- **THEN** файл содержит: обязательные переменные (`TELEGRAM_BOT_TOKEN`, `OWNER_TELEGRAM_ID`), переменные БД (`DATABASE_URL` и раздельные `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`), опциональные API-ключи с пометкой «(опционально)», и опциональные с дефолтами (`TIMEZONE`, `REMINDER_CHECK_INTERVAL_SECONDS`, `MINI_APP_URL`, `MINI_APP_PORT`)
