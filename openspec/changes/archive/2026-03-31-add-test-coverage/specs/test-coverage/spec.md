## ADDED Requirements

### Requirement: Dev-зависимости вынесены в отдельный файл
Проект SHALL иметь файл `requirements-dev.txt`, который включает production-зависимости через `-r requirements.txt` и добавляет dev-зависимости: `pytest`, `pytest-asyncio`, `pytest-cov`.

#### Scenario: Установка dev-зависимостей
- **WHEN** разработчик выполняет `pip install -r requirements-dev.txt`
- **THEN** устанавливаются все production-зависимости и дополнительно `pytest`, `pytest-asyncio`, `pytest-cov`

### Requirement: Конфигурация pytest в pyproject.toml
Проект SHALL содержать `pyproject.toml` с секцией `[tool.pytest.ini_options]`, определяющей: путь к тестам (`tests/`), asyncio_mode (`auto`), и набор маркеров.

#### Scenario: Запуск тестов без дополнительных флагов
- **WHEN** разработчик выполняет `pytest` из корня проекта
- **THEN** pytest автоматически находит тесты в `tests/`, async-тесты выполняются без явного маркера `@pytest.mark.asyncio`

### Requirement: Конфигурация coverage в pyproject.toml
Проект SHALL содержать секции `[tool.coverage.run]` и `[tool.coverage.report]` в `pyproject.toml`. Coverage MUST измерять пакеты `app` и `mini_app`. Из отчёта MUST быть исключены тесты, миграции и файлы `__init__.py`.

#### Scenario: Запуск тестов с измерением покрытия
- **WHEN** разработчик выполняет `pytest --cov`
- **THEN** в терминале выводится таблица покрытия по модулям `app` и `mini_app` с указанием непокрытых строк

#### Scenario: Генерация HTML-отчёта покрытия
- **WHEN** разработчик выполняет `pytest --cov --cov-report=html`
- **THEN** создаётся директория `htmlcov/` с интерактивным HTML-отчётом покрытия

### Requirement: htmlcov исключён из git
Директория `htmlcov/` SHALL быть добавлена в `.gitignore`, чтобы сгенерированные отчёты не попадали в репозиторий.

#### Scenario: Генерация отчёта не создаёт untracked-файлов
- **WHEN** разработчик генерирует HTML-отчёт покрытия
- **THEN** `git status` не показывает `htmlcov/` как untracked-директорию
