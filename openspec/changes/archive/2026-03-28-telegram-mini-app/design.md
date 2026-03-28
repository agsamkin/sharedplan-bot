## Context

Shared Plan Bot — Telegram-бот для совместного планирования событий. Текущий интерфейс управления (редактирование/удаление событий, управление пространствами, настройки напоминаний) реализован через inline-кнопки и FSM-хендлеры aiogram. Это работает, но ограничено: нет списков с прокруткой, нет удобных форм редактирования, каждое действие требует цепочки callback-ов.

Telegram Mini App (WebApp) — встроенный в Telegram веб-интерфейс, который открывается внутри приложения и имеет доступ к авторизации пользователя через `initData`.

Текущая архитектура: однопроцессный async Python (aiogram + SQLAlchemy async + APScheduler), PostgreSQL 16, Docker Compose.

## Goals / Non-Goals

**Goals:**
- Перенести управление событиями (списки, редактирование, удаление) в Mini App
- Перенести управление пространствами (участники, настройки, удаление) в Mini App
- Перенести настройки напоминаний в Mini App
- Сохранить в боте создание событий (текст/голос), создание пространств, присоединение по ссылке, получение напоминаний
- Обеспечить авторизацию через Telegram WebApp initData
- Минимально изменить существующую БД и сервисный слой

**Non-Goals:**
- Переделка существующего сервисного слоя или моделей БД
- Push-уведомления из Mini App (напоминания остаются через бота)
- Мультиязычность интерфейса (только русский)
- PWA-функциональность вне Telegram
- Собственная система аутентификации (только Telegram initData)

## Decisions

### 1. Бэкенд-фреймворк: aiohttp web server

**Выбор:** aiohttp web server, встроенный в тот же процесс что и aiogram бот.

**Почему:** aiohttp уже есть в зависимостях (используется speech_to_text.py). aiogram 3.x внутри использует aiohttp. Добавление web-сервера в тот же event loop позволяет переиспользовать существующие сервисы (`event_service`, `space_service`, `reminder_service`) и DB-сессии напрямую, без дублирования.

**Альтернативы:**
- FastAPI — потребовал бы uvicorn и отдельный процесс или сложную интеграцию с aiogram event loop. Избыточен для REST API без сложной валидации.
- Отдельный процесс — усложнение Docker Compose, дублирование подключения к БД, проблемы с shared state.

### 2. Фронтенд: React + Vite + @telegram-apps/telegram-ui

**Выбор:** React SPA, собираемый через Vite, с использованием официальной библиотеки `@telegram-apps/telegram-ui` для нативного look & feel в Telegram.

**Почему:** React — наиболее поддерживаемый фреймворк в экосистеме Telegram Mini Apps. `@telegram-apps/telegram-ui` предоставляет готовые компоненты (List, Cell, Section, Button, Modal), стилизованные под Telegram. Vite обеспечивает быструю сборку и маленький бандл.

**Альтернативы:**
- Vue/Svelte — меньше поддержки в Telegram SDK экосистеме.
- Vanilla JS — слишком много ручной работы для интерактивного UI.

### 3. Авторизация: Telegram WebApp initData

**Выбор:** Валидация `initData` на каждом API-запросе через HMAC-SHA256 подпись.

**Механизм:**
1. Фронтенд получает `window.Telegram.WebApp.initData` (строка с параметрами, подписанная Telegram)
2. Передаёт в заголовке `Authorization: tma <initData>` каждого запроса
3. Бэкенд валидирует HMAC-SHA256 подпись используя `TELEGRAM_BOT_TOKEN`
4. Извлекает `user.id` из `initData` — это Telegram user ID, который является PK в таблице `users`

**Почему:** Это стандартный механизм авторизации Telegram Mini App. Не требует сессий, JWT или дополнительных хранилищ. User ID из initData напрямую маппится на PK таблицы users.

### 4. Архитектура API: REST endpoints

**Структура эндпоинтов:**

```
GET  /api/spaces                    — список пространств пользователя
GET  /api/spaces/:id                — информация о пространстве + участники
DELETE /api/spaces/:id              — удаление пространства (admin only)
DELETE /api/spaces/:id/members/:uid — удаление участника (admin only)

GET  /api/spaces/:id/events         — список событий пространства
GET  /api/events/:id                — карточка события
PUT  /api/events/:id                — редактирование события (owner only)
DELETE /api/events/:id              — удаление события (owner only)

GET  /api/user/reminders            — текущие настройки напоминаний
PUT  /api/user/reminders            — обновление настроек напоминаний
```

**Почему REST:** Простые CRUD-операции без подписок или сложных связей. REST покрывает все кейсы. GraphQL избыточен.

### 5. Раздача фронтенда: статика через aiohttp

**Выбор:** aiohttp отдаёт собранный фронтенд (dist/) как статические файлы. В Docker фронтенд собирается на этапе build.

**Почему:** Один контейнер, одна точка входа. Не нужен nginx или отдельный сервис для статики. Для масштаба этого проекта (небольшие группы) — достаточно.

**Альтернатива:** nginx reverse proxy — избыточен, добавляет ещё один сервис в Docker Compose.

### 6. Структура проекта: mini_app/ в корне

```
mini_app/
├── backend/
│   ├── __init__.py
│   ├── app.py          # aiohttp web application factory
│   ├── auth.py         # Telegram initData validation
│   ├── routes/
│   │   ├── events.py   # /api/events, /api/spaces/:id/events
│   │   ├── spaces.py   # /api/spaces
│   │   └── user.py     # /api/user/reminders
│   └── middleware.py    # DB session, error handling
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/
│   │   └── hooks/
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
└── README.md
```

**Почему:** Изоляция от существующего кода бота. `mini_app/backend` использует сервисы из `app/services/` через импорт. Фронтенд — отдельная сборка.

### 7. Интеграция с ботом: кнопка открытия Mini App

**Выбор:** В боте добавляется `MenuButton` типа `web_app` и inline-кнопки «Открыть приложение» в ответах на команды `/events`, `/spaces`, `/space_info`, `/reminders`.

**Механизм:** Telegram `WebAppInfo(url=MINI_APP_URL)` — URL настраивается через env-переменную `MINI_APP_URL`.

### 8. HTTPS: через внешний reverse proxy

**Выбор:** Mini App требует HTTPS. Для development — ngrok/cloudflared. Для production — внешний reverse proxy (nginx, Caddy, или облачный LB) перед Docker Compose стеком.

**Почему:** HTTPS-терминация — ответственность инфраструктуры, не приложения. Бот продолжает работать по long-polling без HTTPS.

## Risks / Trade-offs

**[Однопроцессная архитектура]** → Бот и веб-сервер в одном процессе: если один упадёт, упадёт и другой. **Mitigation:** Существующая архитектура и так однопроцессная. Docker restart policy обеспечивает восстановление. Для текущего масштаба (небольшие группы) это допустимо.

**[HTTPS для Mini App]** → Telegram требует HTTPS для Mini App URL. Локальная разработка усложняется. **Mitigation:** Использовать ngrok/cloudflared для туннелирования при разработке. В production — внешний reverse proxy.

**[Размер бандла фронтенда]** → React + UI-библиотека могут дать тяжёлый бандл для мобильного Telegram. **Mitigation:** Vite tree-shaking, lazy loading страниц, мониторинг размера бандла. @telegram-apps/telegram-ui оптимизирован для Mini Apps.

**[Удаление функциональности из бота]** → Пользователи привыкли к inline-кнопкам. **Mitigation:** Плавный переход — сначала добавляем Mini App, затем упрощаем бота. Кнопки-ссылки на Mini App вместо удалённых команд.

**[Уведомления при изменениях через Mini App]** → Когда пользователь редактирует/удаляет событие через Mini App API, участники должны получить уведомление через бота. **Mitigation:** API-хендлеры вызывают существующие сервисы, которые включают отправку уведомлений. Бот-инстанс передаётся в web-приложение при инициализации.

## Migration Plan

1. **Фаза 1 — Бэкенд API:** Добавить aiohttp web server, авторизацию, REST endpoints. Бот продолжает работать как раньше.
2. **Фаза 2 — Фронтенд Mini App:** Создать React SPA с основными страницами (события, пространства, настройки).
3. **Фаза 3 — Интеграция с ботом:** Добавить кнопки открытия Mini App в бота, упростить хендлеры.
4. **Фаза 4 — Очистка:** Удалить из бота устаревшие хендлеры управления.

**Rollback:** Удаление кнопок Mini App из бота и восстановление старых хендлеров (код сохраняется в git).

## Open Questions

- Нужен ли календарный виджет для просмотра событий в Mini App или достаточно списка?
- Стоит ли добавлять тёмную тему Mini App (Telegram предоставляет `themeParams`)?
