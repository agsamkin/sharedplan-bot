## ADDED Requirements

### Requirement: Модуль i18n для бота (Python)
Модуль `app/i18n.py` ДОЛЖЕН содержать словари переводов для языков `ru` и `en`. Функция `t(lang: str, key: str, **kwargs) -> str` ДОЛЖНА возвращать локализованную строку по ключу. При отсутствии ключа в словаре функция ДОЛЖНА возвращать сам ключ как fallback. Словари ДОЛЖНЫ содержать все строки из: `app/bot/formatting.py`, `app/bot/keyboards/`, `app/bot/handlers/`, `app/bot/callbacks/`, `app/bot/middlewares/access_control.py`.

#### Scenario: Получение строки на русском
- **WHEN** вызывается `t("ru", "event.confirm.yes")`
- **THEN** возвращается `"✅ Да"`

#### Scenario: Получение строки на английском
- **WHEN** вызывается `t("en", "event.confirm.yes")`
- **THEN** возвращается `"✅ Yes"`

#### Scenario: Строка с параметрами
- **WHEN** вызывается `t("ru", "space.deleted.notification", name="Семья")`
- **THEN** возвращается строка с подставленным именем пространства

#### Scenario: Отсутствующий ключ (fallback)
- **WHEN** вызывается `t("ru", "nonexistent.key")`
- **THEN** возвращается `"nonexistent.key"`

### Requirement: Модуль i18n для Mini App (React)
Файл `mini_app/frontend/src/i18n.ts` ДОЛЖЕН экспортировать объект переводов с ключами `ru` и `en`. Структура словарей ДОЛЖНА соответствовать макету из `docs/shared-plan-miniapp.jsx` (объект `I18N`). ДОЛЖЕН экспортировать React-хук `useTranslation()`, возвращающий `{ t, language, setLanguage }`, где `t` — словарь текущего языка, `language` — текущий код языка, `setLanguage` — функция смены языка.

#### Scenario: Использование хука в компоненте
- **WHEN** компонент вызывает `useTranslation()` при `language = "ru"`
- **THEN** `t.spaces` возвращает `"Пространства"`, `t.settings` возвращает `"Настройки"`

#### Scenario: Смена языка
- **WHEN** вызывается `setLanguage("en")`
- **THEN** все компоненты, использующие `useTranslation()`, перерендериваются с английскими строками

### Requirement: Поддерживаемые языки
Система ДОЛЖНА поддерживать ровно два языка: `ru` (русский) и `en` (английский). Все прочие значения ДОЛЖНЫ трактоваться как `en`.

#### Scenario: Неизвестный язык нормализуется в en
- **WHEN** система получает `language_code = "de"`
- **THEN** используется язык `en`
