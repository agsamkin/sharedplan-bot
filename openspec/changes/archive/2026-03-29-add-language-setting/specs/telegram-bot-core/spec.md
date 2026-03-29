## MODIFIED Requirements

### Requirement: Middleware обновления профиля пользователя
Middleware `UserProfileMiddleware` обновляет `first_name` и `username` пользователя при каждом входящем сообщении или callback. Регистрируется после `DbSessionMiddleware`. При upsert нового пользователя middleware ДОЛЖЕН определить язык из `language_code` Telegram: если `language_code` начинается с `"ru"` — устанавливает `language = "ru"`, иначе — `language = "en"`. Для существующих пользователей `language` НЕ ДОЛЖЕН перезаписываться. После upsert middleware ДОЛЖЕН передать `data["lang"]` со значением `language` пользователя из БД.

#### Scenario: Новый пользователь с русским Telegram
- **WHEN** пользователь с `language_code = "ru-RU"` впервые взаимодействует с ботом
- **THEN** создаётся запись с `language = "ru"`, `data["lang"] = "ru"`

#### Scenario: Новый пользователь с английским Telegram
- **WHEN** пользователь с `language_code = "en"` впервые взаимодействует с ботом
- **THEN** создаётся запись с `language = "en"`, `data["lang"] = "en"`

#### Scenario: Новый пользователь с неизвестным языком
- **WHEN** пользователь с `language_code = "de"` впервые взаимодействует с ботом
- **THEN** создаётся запись с `language = "en"`, `data["lang"] = "en"`

#### Scenario: Существующий пользователь — язык не перезаписывается
- **WHEN** существующий пользователь с `language = "ru"` отправляет сообщение, а его `language_code` в Telegram сменился на `"en"`
- **THEN** поле `language` в БД остаётся `"ru"`, `data["lang"] = "ru"`

#### Scenario: first_name изменился
- **WHEN** пользователь с изменённым `first_name` отправляет сообщение
- **THEN** `first_name` обновляется, `language` не затрагивается

#### Scenario: username стал NULL
- **WHEN** пользователь удалил username в Telegram
- **THEN** `username` обновляется на NULL, `language` не затрагивается
