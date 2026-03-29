## ADDED Requirements

### Requirement: Проверка доступности сервиса LLM

Функция `parse_event()` ДОЛЖНА проверять наличие `OPENROUTER_API_KEY` в конфигурации перед выполнением запроса. При отсутствии ключа ДОЛЖНА выбрасывать `ParseError` с типом `service_disabled`.

#### Scenario: OPENROUTER_API_KEY отсутствует

- **WHEN** вызывается `parse_event(user_text)` и `settings.OPENROUTER_API_KEY` равен `None`
- **THEN** выбрасывается `ParseError` с `error_type="service_disabled"` без выполнения HTTP-запроса и без инициализации клиента

#### Scenario: OPENROUTER_API_KEY присутствует

- **WHEN** вызывается `parse_event(user_text)` и `settings.OPENROUTER_API_KEY` задан
- **THEN** выполняется стандартный запрос к OpenRouter API
