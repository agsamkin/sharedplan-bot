## MODIFIED Requirements

### Requirement: Навигация и BackButton

Приложение SHALL использовать React Router с маршрутами: `/`, `/spaces/new`, `/spaces/:id`, `/spaces/:id/edit`, `/spaces/:id/members`, `/spaces/:id/events/new`, `/events/:id`, `/settings/reminders`. Telegram BackButton SHALL синхронизироваться с навигацией: скрыт на `/`, показан на всех остальных маршрутах. Нажатие BackButton SHALL вызывать `navigate(-1)`.

#### Scenario: Навигация назад с BackButton
- **WHEN** пользователь на экране `/spaces/:id/events/new` нажимает Telegram BackButton
- **THEN** происходит навигация на `/spaces/:id`

#### Scenario: BackButton скрыт на главном экране
- **WHEN** пользователь на маршруте `/`
- **THEN** Telegram BackButton скрыт
