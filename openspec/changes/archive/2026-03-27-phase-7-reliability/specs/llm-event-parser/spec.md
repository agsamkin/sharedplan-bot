## MODIFIED Requirements

### Requirement: Валидация ответа LLM через Pydantic

Ответ LLM ДОЛЖЕН валидироваться через Pydantic-модель `ParsedEvent`. При невалидном JSON или отсутствующих/некорректных полях ДОЛЖНО выбрасываться исключение `ParseError`. Дополнительно, `event_date` ДОЛЖЕН проверяться на допустимый диапазон: не более 2 лет в будущее от текущей даты. Дата в прошлом НЕ ДОЛЖНА блокироваться на уровне валидации.

#### Scenario: Валидный JSON от LLM
- **WHEN** LLM возвращает `{"title": "Ужин", "date": "2026-03-28", "time": "19:00"}`
- **THEN** создаётся `ParsedEvent` с `title="Ужин"`, `event_date=date(2026,3,28)`, `event_time=time(19,0)`

#### Scenario: JSON с time=null
- **WHEN** LLM возвращает `{"title": "День рождения", "date": "2026-04-05", "time": null}`
- **THEN** создаётся `ParsedEvent` с `event_time=None`

#### Scenario: Невалидный JSON от LLM
- **WHEN** LLM возвращает текст, не являющийся валидным JSON
- **THEN** выбрасывается `ParseError` с типом `invalid_json`

#### Scenario: Отсутствующее обязательное поле
- **WHEN** LLM возвращает `{"title": "Ужин"}` (без поля `date`)
- **THEN** выбрасывается `ParseError` с типом `invalid_json`

#### Scenario: Дата более 2 лет в будущее
- **WHEN** LLM возвращает `{"title": "Событие", "date": "2029-01-01", "time": null}` при текущей дате 2026-03-27
- **THEN** выбрасывается `ParseError` с типом `invalid_json`

#### Scenario: Дата в прошлом — валидация проходит
- **WHEN** LLM возвращает `{"title": "Встреча", "date": "2026-03-20", "time": "15:00"}` при текущей дате 2026-03-27
- **THEN** создаётся `ParsedEvent` с `event_date=date(2026,3,20)` — валидация НЕ блокирует прошедшие даты
