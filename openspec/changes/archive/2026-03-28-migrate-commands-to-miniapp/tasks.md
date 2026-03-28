## 1. Добавление команды /privacy и обновление команд бота

- [x] 1.1 Создать хэндлер `app/bot/handlers/privacy.py` — команда /privacy, отвечает ссылкой на https://telegram.org/privacy
- [x] 1.2 Обновить `app/bot/commands.py` — оставить только help, privacy; /app заменена на MenuButtonWebApp
- [x] 1.3 Зарегистрировать `privacy.router` в `app/main.py`

## 2. Обновление /start и /help

- [x] 2.1 Обновить `app/bot/handlers/start.py` — приветственное сообщение с описанием бота и inline-кнопкой WebApp «Открыть приложение», сохранить join deep link flow
- [x] 2.2 Обновить `app/bot/handlers/help.py` — краткая справка: создание событий (текст/голос), Mini App для управления, список команд (help, app, privacy)

## 3. Удаление неиспользуемых команд и хэндлеров бота

- [x] 3.1 Удалить регистрацию роутеров `space.router`, `events_list.router`, `reminders.router` из `app/main.py`
- [x] 3.2 Удалить файлы хэндлеров: `app/bot/handlers/space.py`, `app/bot/handlers/events_list.py`, `app/bot/handlers/reminders.py`
- [x] 3.3 Оставлен `space_select_cb.router` — используется event creation flow (выбор пространства)
- [x] 3.4 Удалить FSM-состояние `app/bot/states/create_space.py` и его импорты

## 4. API-эндпоинт создания пространства (Mini App Backend)

- [x] 4.1 Добавить эндпоинт `POST /api/spaces` в `mini_app/backend/` — валидация name (не пустое, <= 255 символов), вызов `space_service.create_space()`, ответ 201 с данными пространства
- [x] 4.2 Зарегистрировать маршрут в aiohttp web app (уже зарегистрирован через routes в spaces.py)

## 5. Экран создания пространства (Mini App Frontend)

- [x] 5.1 Создать компонент/страницу `SpaceCreate` — поле ввода названия (placeholder «Например, "Семья" или "Работа"»), кнопка «Создать» (disabled при пустом), подпись про администратора
- [x] 5.2 Добавить маршрут `/spaces/new` в React Router
- [x] 5.3 Добавить кнопку "+" (IconPlus) в хедер экрана списка пространств, навигация на `/spaces/new`
- [x] 5.4 Подключить вызов `POST /api/spaces` при создании, навигацию на `/` и toast «Пространство создано» при успехе
