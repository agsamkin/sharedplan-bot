## ADDED Requirements

### Requirement: Команда /privacy

Обработчик `/privacy` ДОЛЖЕН отправлять сообщение со ссылкой на политику конфиденциальности Telegram. Хэндлер ДОЛЖЕН быть зарегистрирован в отдельном файле `app/bot/handlers/privacy.py`.

#### Scenario: Пользователь отправляет /privacy
- **WHEN** пользователь отправляет `/privacy`
- **THEN** бот отвечает сообщением: «🔒 Политика конфиденциальности:\nhttps://telegram.org/privacy»
