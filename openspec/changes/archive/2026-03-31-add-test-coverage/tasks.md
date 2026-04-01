## 1. Dev-зависимости

- [x] 1.1 Создать `requirements-dev.txt` с `-r requirements.txt` и пакетами `pytest`, `pytest-asyncio`, `pytest-cov`

## 2. Конфигурация

- [x] 2.1 Создать `pyproject.toml` с секцией `[tool.pytest.ini_options]` (testpaths, asyncio_mode=auto)
- [x] 2.2 Добавить в `pyproject.toml` секцию `[tool.coverage.run]` (source = app, mini_app; omit = tests, alembic)
- [x] 2.3 Добавить в `pyproject.toml` секцию `[tool.coverage.report]` (show_missing, exclude_lines, omit)

## 3. Git

- [x] 3.1 Добавить `htmlcov/` в `.gitignore`

## 4. Документация

- [x] 4.1 Обновить секцию Development Commands в `CLAUDE.md` — добавить команды запуска с покрытием

## 5. Верификация

- [x] 5.1 Выполнить `pip install -r requirements-dev.txt` и убедиться, что зависимости установлены
- [x] 5.2 Выполнить `pytest --cov` и убедиться, что отчёт покрытия выводится корректно
