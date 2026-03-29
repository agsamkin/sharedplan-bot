## 1. База данных

- [x] 1.1 Добавить поле `language` (VARCHAR(5), NOT NULL, DEFAULT 'en') в модель User (`app/db/models.py`)
- [x] 1.2 Создать Alembic-миграцию для добавления колонки `language` в таблицу `users`

## 2. Модуль i18n для бота (Python)

- [x] 2.1 Создать `app/i18n.py` с словарями `MESSAGES_RU` и `MESSAGES_EN` и функцией `t(lang, key, **kwargs)`
- [x] 2.2 Перенести все строки из `app/bot/formatting.py` в словари i18n (названия месяцев, дней недели, шаблоны сообщений, ошибки парсинга, ошибки STT)
- [x] 2.3 Перенести все строки из `app/bot/keyboards/` в словари i18n (тексты кнопок: подтверждение, отмена, настройки напоминаний)
- [x] 2.4 Перенести все строки из `app/bot/handlers/` в словари i18n (start, help, event, voice, privacy)
- [x] 2.5 Перенести все строки из `app/bot/callbacks/` в словари i18n (подтверждение событий, выбор пространства)
- [x] 2.6 Перенести строки из `app/bot/middlewares/access_control.py` в словари i18n
- [x] 2.7 Добавить локализованные метки интервалов напоминаний в словари (ru: "За 1 день", en: "1 day before" и т.д.)

## 3. Middleware — определение и передача языка

- [x] 3.1 Обновить `UserProfileMiddleware` (`app/bot/middlewares/user_profile.py`): при upsert нового пользователя определять язык из `language_code` Telegram (ru* → "ru", иначе → "en"), для существующих — не перезаписывать
- [x] 3.2 Передавать `data["lang"]` из middleware во все хендлеры

## 4. Рефакторинг хендлеров бота на i18n

- [x] 4.1 Обновить `app/bot/formatting.py` — все функции форматирования принимают `lang` и используют `t(lang, key)`
- [x] 4.2 Обновить `app/bot/keyboards/` — все клавиатуры принимают `lang` и используют локализованные строки
- [x] 4.3 Обновить `app/bot/handlers/start.py` — использовать `lang` из `data` для приветственных сообщений
- [x] 4.4 Обновить `app/bot/handlers/help.py` — локализованная справка
- [x] 4.5 Обновить `app/bot/handlers/event.py` — локализованные сообщения создания событий
- [x] 4.6 Обновить `app/bot/handlers/voice.py` — локализованные сообщения обработки голоса
- [x] 4.7 Обновить `app/bot/callbacks/` — локализованные ответы на inline-кнопки
- [x] 4.8 Обновить `app/bot/middlewares/access_control.py` — использовать `t()` для сообщений об ошибках
- [x] 4.9 Обновить уведомления (напоминания, события, пространства) — отправлять на языке получателя из БД

## 5. Mini App Backend — API языка

- [x] 5.1 Добавить `GET /api/user/language` в `mini_app/backend/routes/user.py`
- [x] 5.2 Добавить `PUT /api/user/language` с валидацией (только "ru"/"en") в `mini_app/backend/routes/user.py`

## 6. Mini App Frontend — i18n система

- [x] 6.1 Создать `mini_app/frontend/src/i18n.ts` с объектом переводов (ru/en) по структуре макета `I18N` и хуком `useTranslation()`
- [x] 6.2 Добавить `getLanguage()` и `updateLanguage()` в API-клиент (`mini_app/frontend/src/api/`)
- [x] 6.3 Добавить загрузку языка при инициализации приложения (перед рендером контента)

## 7. Mini App Frontend — экран выбора языка

- [x] 7.1 Создать страницу `LanguageSettingsPage` (`/settings/language`) по макету: Section "Язык интерфейса", два варианта с radio-стилем (жирный + галочка для выбранного), PUT на API при выборе
- [x] 7.2 Добавить маршрут `/settings/language` в React Router
- [x] 7.3 Добавить ListItem "Язык" с иконкой IconGlobe в секцию "Настройки" на экране пространств (SpacesPage)

## 8. Mini App Frontend — рефакторинг на i18n

- [x] 8.1 Перевести `SpacesPage` на `useTranslation()`
- [x] 8.2 Перевести `SpaceDetailPage` на `useTranslation()`
- [x] 8.3 Перевести `EventCreatePage` на `useTranslation()`
- [x] 8.4 Перевести `EventDetailPage` (редактирование/удаление) на `useTranslation()`
- [x] 8.5 Перевести `ReminderSettingsPage` на `useTranslation()`
- [x] 8.6 Перевести `SpaceCreatePage` на `useTranslation()`
- [x] 8.7 Перевести `SpaceEditPage` на `useTranslation()`
- [x] 8.8 Перевести `MembersPage` на `useTranslation()`
- [x] 8.9 Перевести `StateViews` (Loading, Error, Empty) на `useTranslation()`
- [x] 8.10 Перевести общие компоненты (Header, Section) на `useTranslation()` при необходимости
