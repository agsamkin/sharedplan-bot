## MODIFIED Requirements

### Requirement: Обработчик /start с upsert пользователя

Команда `/start` ДОЛЖНА отправлять приветственное сообщение и создавать (или обновлять) запись пользователя в таблице `users` по Telegram user ID. При обновлении ДОЛЖНЫ обновляться `first_name` и `username`.

При наличии deep link payload с префиксом `join_` обработчик ДОЛЖЕН перенаправлять на флоу присоединения к пространству вместо отображения приветствия. Upsert пользователя ДОЛЖЕН выполняться в обоих случаях.

#### Scenario: Новый пользователь отправляет /start

- **WHEN** пользователь, отсутствующий в БД, отправляет `/start` без payload
- **THEN** создаётся запись в `users` с Telegram ID, first_name, username и дефолтными `reminder_settings`, и отправляется приветственное сообщение

#### Scenario: Существующий пользователь отправляет /start

- **WHEN** пользователь, уже существующий в БД, отправляет `/start` без payload
- **THEN** обновляются `first_name` и `username` в записи `users`, и отправляется приветственное сообщение

#### Scenario: Пользователь без username отправляет /start

- **WHEN** пользователь без Telegram username отправляет `/start`
- **THEN** создаётся/обновляется запись с `username = NULL`

#### Scenario: /start с deep link join payload

- **WHEN** пользователь отправляет `/start join_abc12345`
- **THEN** выполняется upsert пользователя и запускается флоу присоединения к пространству по invite_code «abc12345»

#### Scenario: /start с невалидным deep link payload

- **WHEN** пользователь отправляет `/start` с payload, не начинающимся на `join_`
- **THEN** выполняется стандартное приветствие (payload игнорируется)
