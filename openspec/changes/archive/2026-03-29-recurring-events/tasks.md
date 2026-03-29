## 1. База данных

- [x] 1.1 Добавить поля `recurrence_rule` (VARCHAR 20, nullable) и `parent_event_id` (UUID, nullable FK → events.id ON DELETE CASCADE) в модель Event в `app/db/models.py`
- [x] 1.2 Создать Alembic-миграцию для новых колонок и индекса `idx_events_parent`
- [x] 1.3 Применить миграцию и проверить схему

## 2. Сервис повторяющихся событий

- [x] 2.1 Создать `app/services/recurrence_service.py` с функцией вычисления следующей даты (`next_occurrence_date`) для каждого типа повторения (daily, weekly, biweekly, monthly, yearly) с использованием `dateutil.relativedelta`
- [x] 2.2 Добавить функцию `generate_occurrences(session, event, horizon_days=60)` — генерация дочерних вхождений с проверкой на дубликаты по `parent_event_id + event_date`
- [x] 2.3 Добавить функцию `regenerate_occurrences(session, parent_event)` — удаление будущих дочерних вхождений и генерация заново (для изменения recurrence_rule)
- [x] 2.4 Добавить функцию `update_future_occurrences(session, parent_event)` — обновление title/time у будущих дочерних вхождений

## 3. Интеграция с сервисом напоминаний

- [x] 3.1 Обновить `reminder_service.create_reminders_for_event()` — вызывать для каждого сгенерированного вхождения
- [x] 3.2 Обновить `reminder_service.recreate_reminders_for_event()` — обрабатывать каскадное пересоздание для серии

## 4. LLM-парсер

- [x] 4.1 Добавить поле `recurrence_rule` (Optional[str]) в `ParsedEvent` модель в `app/services/llm_parser.py` с валидацией допустимых значений
- [x] 4.2 Обновить системный промпт в `app/prompts/event_parser.py` — добавить описание поля `recurrence_rule` в JSON-формат, правила распознавания повторений, few-shot примеры с повторениями

## 5. Бот — создание событий

- [x] 5.1 Обновить `app/bot/handlers/event.py` — сохранять `recurrence_rule` из ParsedEvent в FSM-состояние, передавать при создании
- [x] 5.2 Обновить карточку подтверждения — добавить строку `🔄 {repeat_label}` для повторяющихся событий
- [x] 5.3 Обновить `app/bot/callbacks/event_confirm.py` — при подтверждении вызывать генерацию вхождений для повторяющихся событий
- [x] 5.4 Обновить уведомления участникам — добавить информацию о повторении
- [x] 5.5 Добавить i18n-строки для меток повторения в бот-сообщениях (ru/en)

## 6. Бот — управление событиями

- [x] 6.1 Обновить обработку удаления — предупреждение о серии для повторяющихся событий

## 7. Mini App Backend

- [x] 7.1 Обновить `POST /api/spaces/:space_id/events` — принимать `recurrence_rule`, генерировать вхождения при создании
- [x] 7.2 Обновить `GET /api/spaces/:space_id/events` — возвращать `recurrence_rule` и `parent_event_id`, фильтровать дочерние вхождения из списка
- [x] 7.3 Обновить `GET /api/events/:event_id` — возвращать `recurrence_rule` и `parent_event_id`
- [x] 7.4 Обновить `PUT /api/events/:event_id` — обрабатывать изменение `recurrence_rule` (пересоздание вхождений), обновлять будущие вхождения при изменении title/time
- [x] 7.5 Обновить `DELETE /api/events/:event_id` — каскадное удаление уже обеспечено FK, убедиться что уведомления корректны

## 8. Mini App Frontend — i18n и API

- [x] 8.1 Добавить i18n-строки: `repeat`, `repeatOptions` (none, daily, weekly, biweekly, monthly, yearly) для ru и en
- [x] 8.2 Обновить API-клиент `mini_app/frontend/src/api/events.ts` — добавить `recurrence_rule` в типы и запросы create/update

## 9. Mini App Frontend — UI компоненты

- [x] 9.1 Создать компонент RepeatPicker на основе макета из `docs/shared-plan-miniapp.jsx` (выпадающий селектор с IconRepeat, подсветка выбранного значения)
- [x] 9.2 Добавить иконку IconRepeat (SVG из макета)

## 10. Mini App Frontend — страницы

- [x] 10.1 Обновить EventCreatePage — добавить RepeatPicker, передавать `recurrence_rule` при создании
- [x] 10.2 Обновить EventDetailPage (редактирование) — добавить RepeatPicker, передавать `recurrence_rule` при сохранении
- [x] 10.3 Обновить отображение событий в SpaceDetailPage — показывать метку повторения в подзаголовке
- [x] 10.4 Обновить диалог удаления — предупреждение о серии для повторяющихся событий

## 11. Планировщик — фоновая генерация

- [x] 11.1 Добавить задачу `generate_recurring_occurrences()` в `app/scheduler/jobs.py` — ежедневная генерация недостающих вхождений на 60 дней
- [x] 11.2 Зарегистрировать задачу в `app/main.py` через APScheduler (interval: раз в сутки)

## 12. Тестирование

- [x] 12.1 Тесты для `recurrence_service` — вычисление дат, генерация вхождений, edge cases (конец месяца, 29 февраля)
- [x] 12.2 Тесты для LLM-парсера — валидация recurrence_rule, парсинг промптов
- [x] 12.3 Тесты для API-эндпоинтов — создание/редактирование/удаление повторяющихся событий
- [x] 12.4 Тесты для фоновой генерации — идемпотентность, корректность напоминаний
