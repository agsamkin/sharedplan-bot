## Why

Фаза 1 создала скелет: бот стартует, БД с таблицами готова, `/start` и `/help` работают. Но пользователи пока не могут организовывать совместные календари — нет механизма создания пространств, приглашения участников и управления ими. Пространства — основная организационная единица проекта, без которой невозможны события (Фаза 3) и всё, что строится поверх.

## What Changes

- Команда `/newspace` — FSM-флоу создания пространства (запрос названия → генерация invite-кода → создание записей в `spaces` + `user_spaces`)
- Deep link обработка в `/start` — парсинг payload `join_<invite_code>`, добавление пользователя в пространство, уведомление текущих участников
- Команда `/spaces` — список пространств пользователя с ролью и количеством участников
- Команда `/space_info` — детальная информация о пространстве (участники, invite-ссылка), с выбором пространства если их несколько
- Команда `/kick @username` — удаление участника из пространства (только для админа)
- Команда `/delete_space` — удаление пространства с inline-подтверждением (только для админа, каскадное удаление)
- Сервисный слой `services/space_service.py` — вся бизнес-логика пространств
- Inline-клавиатура выбора пространства `keyboards/space_select.py`
- Callback-обработчик `callbacks/space_select.py`
- FSM-состояние `CreateSpace.waiting_for_name` в `bot/states/create_space.py`
- Фильтр `filters/not_command.py` — определяет, что сообщение не является командой (понадобится в Фазе 3)

## Capabilities

### New Capabilities

- `space-management`: Полный жизненный цикл пространств — создание через FSM, генерация invite-ссылки, просмотр списка и информации, администрирование (kick, удаление)
- `space-joining`: Присоединение к пространству по deep link (`/start join_<invite_code>`), уведомление участников о новом члене, обработка ошибок (невалидный код, уже участник)

### Modified Capabilities

- `telegram-bot-core`: Обработчик `/start` расширяется deep link логикой — при наличии payload `join_<invite_code>` запускается флоу присоединения вместо приветствия

## Impact

- **Новые файлы**: `app/bot/handlers/space.py`, `app/services/space_service.py`, `app/bot/keyboards/space_select.py`, `app/bot/callbacks/space_select.py`, `app/bot/states/create_space.py`, `app/bot/filters/not_command.py`
- **Изменяемые файлы**: `app/bot/handlers/start.py` (deep link), `app/main.py` (подключение новых роутеров)
- **Зависимости**: нет новых Python-пакетов (всё уже есть: aiogram FSM, SQLAlchemy)
- **БД**: таблицы `spaces`, `user_spaces` уже созданы в Фазе 1 — новых миграций не требуется
