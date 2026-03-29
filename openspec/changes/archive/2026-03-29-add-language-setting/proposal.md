## Why

Бот и Mini App работают только на русском языке. Все строки захардкожены в коде — в хендлерах, форматировании, клавиатурах, компонентах фронтенда. Пользователи, которые используют Telegram на английском, получают интерфейс полностью на русском без возможности выбора. Добавление настройки языка (ru/en) улучшит UX для англоязычных пользователей и заложит фундамент для дальнейшей локализации.

## What Changes

- Добавить поле `language` в модель `User` (VARCHAR, default определяется из Telegram `language_code`)
- Создать систему i18n-словарей для бота (Python) и Mini App (React)
- Извлечь все захардкоженные строки бота в словари (`ru`, `en`)
- Извлечь все захардкоженные строки Mini App frontend в словари (`ru`, `en`)
- Добавить API-эндпоинт для получения/обновления языка пользователя
- Добавить экран выбора языка в Mini App (по макету из `docs/shared-plan-miniapp.jsx`)
- Определять язык автоматически при первом запуске по `language_code` из Telegram. Fallback — `en`

## Capabilities

### New Capabilities
- `i18n`: система интернационализации — словари переводов (ru/en), определение языка пользователя, API и UI для переключения языка

### Modified Capabilities
- `database-schema`: добавление поля `language` в таблицу `users`
- `mini-app-frontend`: новый экран выбора языка, переход всех компонентов на i18n-словари
- `mini-app-backend`: новый эндпоинт `/api/user/language` (GET/PUT), передача языка в API-ответы
- `telegram-bot-core`: middleware для определения/инъекции языка пользователя
- `reminder-settings`: локализация лейблов интервалов напоминаний

## Impact

- **БД**: миграция — добавление колонки `language VARCHAR(5) DEFAULT 'en'` в `users`
- **Бот (Python)**: затрагивает `app/bot/handlers/`, `app/bot/formatting.py`, `app/bot/keyboards/`, `app/bot/callbacks/`, `app/bot/middlewares/user_profile.py`, `app/bot/middlewares/access_control.py`
- **Mini App backend**: затрагивает `mini_app/backend/routes/user.py`
- **Mini App frontend**: затрагивает все компоненты в `mini_app/frontend/src/pages/` и `mini_app/frontend/src/components/`
- **Зависимости**: не требуется новых пакетов — используются простые словари
