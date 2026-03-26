## 1. Сервисный слой

- [x] 1.1 Создать `app/services/space_service.py` с функциями: `create_space(session, user_id, name) → Space`, `get_user_spaces(session, user_id) → list`, `get_space_info(session, space_id) → dict`, `get_space_by_invite_code(session, invite_code) → Space | None`, `join_space(session, user_id, space_id) → UserSpace`, `get_space_members(session, space_id) → list`, `kick_member(session, space_id, target_user_id)`, `delete_space(session, space_id)`, `check_admin(session, space_id, user_id) → bool`, `find_member_by_username(session, space_id, username) → UserSpace | None`
- [x] 1.2 Реализовать генерацию invite-кода через `secrets.token_urlsafe(6)` с retry при коллизии (IntegrityError)

## 2. FSM и фильтры

- [x] 2.1 Создать `app/bot/states/create_space.py` с FSM-состоянием `CreateSpace.waiting_for_name`
- [x] 2.2 Создать `app/bot/filters/not_command.py` — фильтр, определяющий что сообщение не команда (не начинается с `/`)

## 3. Клавиатуры и callbacks

- [x] 3.1 Создать `app/bot/keyboards/space_select.py` — генерация inline-клавиатуры выбора пространства с callback data `space_select:{space_id}:{action}`
- [x] 3.2 Создать `app/bot/keyboards/confirm.py` — inline-кнопки подтверждения удаления пространства (`delete_space_confirm:{space_id}` / `delete_space_cancel:{space_id}`)
- [x] 3.3 Создать `app/bot/callbacks/space_select.py` — обработчик callback `space_select:*`, маршрутизация по action

## 4. Handlers — создание и просмотр пространств

- [x] 4.1 Создать `app/bot/handlers/space.py` с обработчиком `/newspace` — установка FSM-состояния, запрос названия
- [x] 4.2 Добавить handler для FSM-состояния `CreateSpace.waiting_for_name` — валидация названия (1–255 символов, не пустое), вызов `space_service.create_space`, ответ с invite-ссылкой
- [x] 4.3 Добавить обработчик `/spaces` — вызов `space_service.get_user_spaces`, форматирование списка с ролью и количеством участников
- [x] 4.4 Добавить обработчик `/space_info` — если одно пространство: показать info, если несколько: показать inline-клавиатуру выбора. Callback обработчик для показа info после выбора.

## 5. Handlers — администрирование

- [x] 5.1 Добавить обработчик `/kick @username` — парсинг username из message.text, проверка admin-роли, поиск участника, удаление через `space_service.kick_member`
- [x] 5.2 Добавить обработчик `/delete_space` — проверка admin-роли, показ inline-подтверждения, callback для подтверждения/отмены, вызов `space_service.delete_space`

## 6. Deep link — присоединение к пространству

- [x] 6.1 Модифицировать `app/bot/handlers/start.py` — добавить обработчик `/start` с deep link payload `join_*`: upsert пользователя, вызов `space_service.get_space_by_invite_code`, `space_service.join_space`, уведомление участников
- [x] 6.2 Обработать edge cases: невалидный invite-код, пользователь уже участник, формирование invite-ссылки через `bot.get_me().username`

## 7. Интеграция

- [x] 7.1 Подключить роутер `space.py` в `app/main.py` (include_router)
- [x] 7.2 Проверить что все новые модули имеют корректные `__init__.py` (при необходимости) и импорты
