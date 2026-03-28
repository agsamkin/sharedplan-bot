## MODIFIED Requirements

### Requirement: Команда /reminders — ссылка на Mini App

Обработчик команды `/reminders` ДОЛЖЕН направлять пользователя в Mini App для настройки напоминаний.

#### Scenario: Пользователь вызывает /reminders
- **WHEN** пользователь отправляет команду `/reminders`
- **THEN** бот отвечает сообщением «Настрой напоминания в приложении:» с inline-кнопкой WebApp «⏰ Настройки напоминаний» со ссылкой на Mini App (маршрут `/settings/reminders`)

## REMOVED Requirements

### Requirement: Inline-клавиатура с toggle-кнопками
**Reason**: Настройки напоминаний перенесены в Mini App, где доступны полноценные toggle-переключатели.
**Migration**: Реализована в `mini-app-frontend` спеке (страница настроек напоминаний).

### Requirement: Переключение настройки по нажатию кнопки
**Reason**: Toggle-логика перенесена в Mini App frontend + backend API.
**Migration**: `PUT /api/user/reminders` в `mini-app-backend`, toggle UI в `mini-app-frontend`.
