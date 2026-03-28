## 1. Конфигурация и инфраструктура

- [x] 1.1 Добавить `MINI_APP_URL` и `MINI_APP_PORT` в `app/config.py` (pydantic-settings)
- [x] 1.2 Создать структуру директорий `mini_app/backend/` и `mini_app/frontend/`
- [x] 1.3 Обновить `Dockerfile` — добавить multi-stage build (Node.js для фронтенда + Python)
- [x] 1.4 Обновить `docker-compose.yml` — проброс порта `MINI_APP_PORT`
- [x] 1.5 Обновить `.env.example` с новыми переменными

## 2. Бэкенд: авторизация и middleware

- [x] 2.1 Создать `mini_app/backend/auth.py` — валидация Telegram initData (HMAC-SHA256), извлечение user_id
- [x] 2.2 Создать `mini_app/backend/middleware.py` — auth middleware (проверка Authorization header), DB session middleware, error handling middleware
- [x] 2.3 Написать тесты для валидации initData

## 3. Бэкенд: REST API пространств

- [x] 3.1 Создать `mini_app/backend/routes/spaces.py` — `GET /api/spaces` (список пространств пользователя)
- [x] 3.2 Реализовать `GET /api/spaces/:id` (информация о пространстве + участники)
- [x] 3.3 Реализовать `DELETE /api/spaces/:id` (удаление пространства, admin only)
- [x] 3.4 Реализовать `DELETE /api/spaces/:id/members/:uid` (удаление участника, admin only)

## 4. Бэкенд: REST API событий

- [x] 4.1 Создать `mini_app/backend/routes/events.py` — `GET /api/spaces/:id/events` (список событий пространства)
- [x] 4.2 Реализовать `GET /api/events/:id` (карточка события)
- [x] 4.3 Реализовать `PUT /api/events/:id` (редактирование события, owner only) с пересозданием напоминаний и отправкой уведомлений через бота
- [x] 4.4 Реализовать `DELETE /api/events/:id` (удаление события, owner only) с каскадным удалением и уведомлениями

## 5. Бэкенд: REST API настроек

- [x] 5.1 Создать `mini_app/backend/routes/user.py` — `GET /api/user/reminders` (текущие настройки)
- [x] 5.2 Реализовать `PUT /api/user/reminders` (обновление настроек, merge-подход)

## 6. Бэкенд: aiohttp приложение и интеграция

- [x] 6.1 Создать `mini_app/backend/app.py` — фабрика aiohttp web application, подключение routes и middleware, раздача статики
- [x] 6.2 Интегрировать запуск aiohttp web server в `app/main.py` — одновременный запуск с aiogram long-polling
- [x] 6.3 Передать экземпляр `Bot` в aiohttp app context для отправки уведомлений из API

## 7. Фронтенд: инициализация проекта

- [x] 7.1 Инициализировать React + Vite + TypeScript проект в `mini_app/frontend/`
- [x] 7.2 Установить зависимости: `@telegram-apps/sdk-react`, `@telegram-apps/telegram-ui`, `react-router-dom`
- [x] 7.3 Настроить Vite: proxy для `/api` в dev-режиме, output в `dist/`
- [x] 7.4 Создать `App.tsx` — инициализация Telegram SDK, применение темы, настройка роутера

## 8. Фронтенд: API-слой и утилиты

- [x] 8.1 Создать `api/client.ts` — fetch-обёртка с `Authorization: tma <initData>` и обработкой ошибок
- [x] 8.2 Создать `api/spaces.ts`, `api/events.ts`, `api/user.ts` — типизированные API-функции
- [x] 8.3 Создать `utils/dates.ts` — относительные даты на русском (сегодня, завтра, день недели, числовая дата)

## 9. Фронтенд: страницы

- [x] 9.1 Создать страницу списка пространств (`pages/SpacesPage.tsx`) — главная страница Mini App
- [x] 9.2 Создать страницу событий пространства (`pages/SpaceEventsPage.tsx`) — список событий с кнопками управления для владельца
- [x] 9.3 Создать страницу/модалку редактирования события (`pages/EventEditPage.tsx`) — форма с title, date picker, time picker, чекбокс «весь день»
- [x] 9.4 Создать страницу управления пространством (`pages/SpaceSettingsPage.tsx`) — участники, invite-ссылка, удаление
- [x] 9.5 Создать страницу настроек напоминаний (`pages/ReminderSettingsPage.tsx`) — 6 toggle-переключателей

## 10. Фронтенд: UX-компоненты

- [x] 10.1 Создать компонент подтверждения удаления (диалог с «Удалить» / «Отмена»)
- [x] 10.2 Создать компоненты состояний: загрузка (скелетон), ошибка (с кнопкой «Повторить»), пустой список
- [x] 10.3 Настроить навигацию: кнопка «Назад» Telegram, react-router history

## 11. Обновление бота

- [x] 11.1 Обновить `app/bot/commands.py` — убрать `/reminders`, `/space_info` из меню, добавить `/app`
- [x] 11.2 Создать хендлер `/app` — отправка inline-кнопки WebApp
- [x] 11.3 Упростить `/events` — заменить список событий на кнопку открытия Mini App
- [x] 11.4 Упростить `/spaces` — добавить кнопку «Управление пространствами» (WebApp)
- [x] 11.5 Упростить `/space_info` — перенаправление в Mini App
- [x] 11.6 Упростить `/reminders` — перенаправление в Mini App
- [x] 11.7 Удалить устаревшие callback-хендлеры: `event_manage.py`, `reminder_toggle.py`
- [x] 11.8 Удалить устаревшие состояния FSM: `EditEvent`

## 12. Финализация

- [x] 12.1 Обновить `requirements.txt` (если нужны новые Python-зависимости)
- [x] 12.2 Проверить сборку Docker-образа и запуск полного стека (ручная проверка)
- [x] 12.3 Проверить работу Mini App через ngrok/cloudflared (HTTPS) (ручная проверка)
