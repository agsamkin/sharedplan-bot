## ADDED Requirements

### Requirement: Проверка доступности сервиса STT

Функция `transcribe()` ДОЛЖНА проверять наличие `NEXARA_API_KEY` в конфигурации перед выполнением запроса. При отсутствии ключа ДОЛЖНА выбрасывать `TranscriptionError` с типом `service_disabled`.

#### Scenario: NEXARA_API_KEY отсутствует

- **WHEN** вызывается `transcribe(audio_bytes)` и `settings.NEXARA_API_KEY` равен `None`
- **THEN** выбрасывается `TranscriptionError` с `error_type="service_disabled"` без выполнения HTTP-запроса

#### Scenario: NEXARA_API_KEY присутствует

- **WHEN** вызывается `transcribe(audio_bytes)` и `settings.NEXARA_API_KEY` задан
- **THEN** выполняется стандартный запрос к Nexara API

## MODIFIED Requirements

### Requirement: Класс исключения TranscriptionError

Модуль ДОЛЖЕН определять класс `TranscriptionError(Exception)` с атрибутом `error_type: str` для типизированной обработки ошибок в хендлере.

Возможные значения `error_type`: `timeout`, `service_unavailable`, `auth_error`, `bad_request`, `empty_result`, `service_disabled`.

#### Scenario: TranscriptionError содержит тип ошибки

- **WHEN** возникает ошибка транскрипции
- **THEN** `TranscriptionError` содержит `error_type` с одним из определённых значений и текстовое описание ошибки
