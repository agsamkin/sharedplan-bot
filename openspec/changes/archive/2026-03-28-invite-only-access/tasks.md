## 1. Конфигурация

- [x] 1.1 Добавить поле `OWNER_TELEGRAM_ID: int` в `app/config.py` (класс `Settings`)
- [x] 1.2 Добавить `OWNER_TELEGRAM_ID` в `.env.example` с комментарием
- [x] 1.3 Добавить `OWNER_TELEGRAM_ID` в `.env` (актуальное значение)

## 2. Middleware контроля доступа

- [x] 2.1 Создать `app/bot/middlewares/access_control.py` с классом `AccessControlMiddleware`
- [x] 2.2 Реализовать логику проверки: owner → deep link join → space member → block
- [x] 2.3 Реализовать fail-closed поведение при ошибках БД
- [x] 2.4 Реализовать ответ на callback_query от неавторизованных («Доступ запрещён»)

## 3. Регистрация middleware

- [x] 3.1 Зарегистрировать `AccessControlMiddleware` в `app/main.py` между `DbSessionMiddleware` и `UserProfileMiddleware`

## 4. Обновление сопутствующего кода

- [x] 4.1 Обновить список команд в `app/bot/commands.py` если необходимо
- [x] 4.2 Обновить текст помощи в `app/bot/handlers/help.py` — указать что бот приватный

## 5. Проверка

- [x] 5.1 Проверить что бот запускается с новой конфигурацией
- [ ] 5.2 Проверить что неавторизованный пользователь получает сообщение о приватности
- [ ] 5.3 Проверить что deep link join работает для новых пользователей
- [ ] 5.4 Проверить что владелец имеет полный доступ без пространств
