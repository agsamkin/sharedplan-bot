## Why

Бот перегружен командами (/newspace, /spaces, /space_info, /events, /reminders), которые дублируют функциональность Mini App. Пользователям неудобно пользоваться множеством команд — Mini App предоставляет более наглядный и удобный интерфейс для управления пространствами и событиями. Нужно упростить бота до минимума команд (/start, /help, /privacy) и перенести создание пространств в Mini App.

## What Changes

- **BREAKING**: Удаление команд `/newspace`, `/spaces`, `/space_info`, `/events`, `/reminders` из бота
- **BREAKING**: Удаление хэндлеров и FSM-состояний, связанных с удалёнными командами
- Обновление `/start` — приветственное сообщение с кнопкой открытия Mini App
- Обновление `/help` — справка только по оставшимся командам и описание Mini App
- Добавление команды `/privacy` — ссылка на https://telegram.org/privacy
- Обновление регистрации команд в BotFather (только start, help, privacy)
- Добавление экрана создания пространства в Mini App (по макету из `shared-plan-miniapp.jsx`)
- Добавление API-эндпоинта `POST /api/spaces` для создания пространства из Mini App

## Capabilities

### New Capabilities
- `bot-privacy-command`: Команда /privacy — отправляет ссылку на политику конфиденциальности Telegram

### Modified Capabilities
- `bot-commands-menu`: Удаление команд newspace, spaces, space_info, events, reminders; добавление privacy; start и help скрыты из меню (start невидима по умолчанию, help остаётся)
- `telegram-bot-core`: Обновление регистрации роутеров — удаление роутеров удалённых команд, добавление роутера privacy
- `space-management`: Удаление хэндлера /newspace и FSM CreateSpace; создание пространств теперь только через Mini App API
- `mini-app-frontend`: Добавление экрана spaceCreate с формой ввода названия пространства (по макету)
- `mini-app-backend`: Добавление эндпоинта POST /api/spaces для создания пространства

## Impact

- **Хэндлеры бота**: Удаление `space.py` (или рефакторинг — оставить только join-flow в start.py), `events_list.py`, `reminders.py`; обновление `help.py`, `start.py`
- **FSM-состояния**: Удаление `CreateSpace` из `app/bot/states/create_space.py`
- **Команды**: Обновление `app/bot/commands.py` — оставить только start, help, privacy
- **Callback-хэндлеры**: Удаление `space_select_cb` (больше не нужен для выбора пространства через бота)
- **Mini App Frontend**: Новый экран `spaceCreate` с навигацией из списка пространств (кнопка "+")
- **Mini App Backend**: Новый эндпоинт, использующий существующий `space_service.create_space()`
- **Пользователи**: Ломающее изменение UX — привычные команды перестанут работать, нужно перенаправление в Mini App
