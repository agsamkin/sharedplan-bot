## MODIFIED Requirements

### Requirement: LLM client
Модуль `services/llm_parser.py` ДОЛЖЕН предоставлять async-функцию `parse_event(user_text: str) -> ParsedEvent`. Использует `openai.AsyncOpenAI` с `base_url` OpenRouter. Клиент инициализируется лениво при первом вызове. Возвращает `ParsedEvent` с полями: `title` (str), `event_date` (date, alias "date"), `event_time` (Optional[time], alias "time"), `recurrence_rule` (Optional[str], alias "recurrence_rule"). Валидация: дата не дальше ±2 лет, `recurrence_rule` принимает только `daily`, `weekly`, `biweekly`, `monthly`, `yearly` или `null`.

#### Scenario: Парсинг текста с повторением
- **WHEN** пользователь отправляет "встреча каждый вторник в 15:00"
- **THEN** парсер возвращает `ParsedEvent(title="Встреча", event_date=<ближайший вторник>, event_time=15:00, recurrence_rule="weekly")`

#### Scenario: Парсинг текста без повторения
- **WHEN** пользователь отправляет "ужин завтра в 19:00"
- **THEN** парсер возвращает `ParsedEvent(title="Ужин", event_date=<завтра>, event_time=19:00, recurrence_rule=null)`

#### Scenario: Невалидное значение recurrence_rule
- **WHEN** LLM возвращает `recurrence_rule` со значением не из допустимого списка
- **THEN** валидация Pydantic отклоняет ответ и срабатывает retry с усиленным промптом

### Requirement: System prompt
Модуль `prompts/event_parser.py` ДОЛЖЕН формировать системный промпт с: текущей датой, днём недели, временем (Europe/Moscow), JSON-форматом включая поле `recurrence_rule`, инструкцией по вычислению относительных дат, напоминанием «завтра = {дата}». Динамические few-shot примеры ДОЛЖНЫ включать: простая дата+время, день недели, без времени, разговорное время, неявный заголовок, сложная относительная дата, время через дефис, временной диапазон, сегодня+разговорное время, относительное время, **повторение (каждую неделю)**, **повторение (ежемесячно)**, **повторение (каждый день)**, **без повторения (явно одноразовое)**. Правила распознавания повторений: "каждый день/ежедневно" → daily, "каждую неделю/еженедельно/каждый <день_недели>" → weekly, "каждые две недели/раз в две недели" → biweekly, "каждый месяц/ежемесячно/раз в месяц" → monthly, "каждый год/ежегодно/раз в год" → yearly. Если повторение не упомянуто → `null`.

#### Scenario: Промпт содержит примеры повторений
- **WHEN** формируется системный промпт
- **THEN** он включает few-shot примеры с `recurrence_rule` для каждого типа повторения и пример без повторения

#### Scenario: JSON-формат включает recurrence_rule
- **WHEN** формируется описание JSON-формата в промпте
- **THEN** формат описывает поле `"recurrence_rule": "weekly" | "daily" | "biweekly" | "monthly" | "yearly" | null`
