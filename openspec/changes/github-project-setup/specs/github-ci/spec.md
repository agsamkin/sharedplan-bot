## ADDED Requirements

### Requirement: GitHub Actions CI workflow

В репозитории ДОЛЖЕН существовать файл `.github/workflows/ci.yml`, запускающий CI-пайплайн при push и pull request на ветку `main`.

#### Scenario: CI запускается при push в main
- **WHEN** выполняется push в ветку `main`
- **THEN** GitHub Actions запускает workflow CI

#### Scenario: CI запускается при pull request в main
- **WHEN** создаётся pull request в ветку `main`
- **THEN** GitHub Actions запускает workflow CI

### Requirement: Сборка Docker-образа в CI

CI workflow ДОЛЖЕН включать шаг сборки Docker-образа для проверки что Dockerfile корректен.

#### Scenario: Docker build выполняется успешно
- **WHEN** CI workflow запускается
- **THEN** Docker-образ собирается без ошибок через `docker build`

### Requirement: Запуск тестов в CI

CI workflow ДОЛЖЕН запускать `pytest` с PostgreSQL service container для выполнения тестов.

#### Scenario: Тесты запускаются с реальной PostgreSQL
- **WHEN** CI workflow выполняет шаг тестов
- **THEN** PostgreSQL 16 запущен как service container, `pytest` выполняется с `DATABASE_URL` указывающим на этот контейнер

### Requirement: Отчёт покрытия в CI

CI workflow ДОЛЖЕН генерировать отчёт покрытия кода через `pytest --cov` и сохранять его как артефакт.

#### Scenario: Coverage report генерируется
- **WHEN** тесты завершаются успешно
- **THEN** CI генерирует отчёт покрытия и загружает его как GitHub Actions artifact
