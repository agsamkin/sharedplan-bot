## MODIFIED Requirements

### Requirement: Точка входа в main.py

Модуль `app/main.py` ДОЛЖЕН быть точкой входа: создание Bot, Dispatcher, подключение роутеров и middleware, запуск Alembic миграций, запуск long-polling. ДОЛЖНЫ быть зарегистрированы роутеры обработчиков событий (`event.py`, `events_list.py`) и callback-обработчиков (`event_confirm.py`).

#### Scenario: Запуск приложения
- **WHEN** выполняется `python -m app.main`
- **THEN** применяются миграции, регистрируются все роутеры (включая event, events_list, event_confirm), регистрируются middleware, запускается long-polling

#### Scenario: Роутер событий зарегистрирован
- **WHEN** бот запущен
- **THEN** текстовые сообщения (не команды) маршрутизируются к обработчику событий в `handlers/event.py`

#### Scenario: Роутер списка событий зарегистрирован
- **WHEN** бот запущен
- **THEN** команда `/events` маршрутизируется к обработчику в `handlers/events_list.py`
