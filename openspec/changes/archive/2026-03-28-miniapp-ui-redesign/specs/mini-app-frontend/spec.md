## MODIFIED Requirements

### Requirement: Инициализация Mini App
Приложение SHALL инициализировать Telegram WebApp (`ready()`, `expand()`), определять тему (`colorScheme`) и применять соответствующий набор CSS-переменных дизайн-системы. Приложение SHALL НЕ использовать `@telegram-apps/telegram-ui` и `AppRoot`. Обёртка SHALL применять системный шрифт (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`).

#### Scenario: Запуск в light mode
- **WHEN** Mini App открывается с `colorScheme: 'light'`
- **THEN** применяется светлая тема с bg #f2f2f7, text #1a1a1a

#### Scenario: Запуск в dark mode
- **WHEN** Mini App открывается с `colorScheme: 'dark'`
- **THEN** применяется тёмная тема с инвертированными значениями, контраст текста >= 4.5:1

### Requirement: Навигация и BackButton
Приложение SHALL использовать React Router с маршрутами: `/`, `/spaces/:id`, `/spaces/:id/edit`, `/spaces/:id/members`, `/events/:id`, `/settings/reminders`. Telegram BackButton SHALL синхронизироваться с навигацией: скрыт на `/`, показан на всех остальных маршрутах. Нажатие BackButton SHALL вызывать `navigate(-1)`.

#### Scenario: Навигация назад с BackButton
- **WHEN** пользователь на экране `/spaces/1` нажимает Telegram BackButton
- **THEN** происходит навигация на `/`

#### Scenario: BackButton скрыт на главном экране
- **WHEN** пользователь на маршруте `/`
- **THEN** Telegram BackButton скрыт

### Requirement: Экран списка пространств
Экран `/` SHALL отображать список пространств пользователя в Section без заголовка. Каждое пространство SHALL отображаться как ListItem с Avatar (имя пространства, id), названием, подписью «N участн. · M событий», ChevronRight справа. Под списком пространств SHALL отображаться Section «Настройки» с ListItem «Напоминания» (IconBell, подпись «Настроить интервалы»). При загрузке SHALL показываться loading-состояние, при ошибке — error с кнопкой повтора, при пустом списке — empty-состояние.

#### Scenario: Список из 3 пространств
- **WHEN** у пользователя 3 пространства
- **THEN** отображаются 3 ListItem с аватарами, разделённые Divider, и секция «Настройки» ниже

#### Scenario: Переход в пространство
- **WHEN** пользователь нажимает на пространство «Семья»
- **THEN** навигация на `/spaces/1`

#### Scenario: Переход к напоминаниям
- **WHEN** пользователь нажимает «Напоминания»
- **THEN** навигация на `/settings/reminders`

### Requirement: Экран напоминаний
Экран `/settings/reminders` SHALL отображать Section «Интервалы напоминаний» с 6 строками: каждая содержит текст интервала и Toggle. Под секцией SHALL быть подпись (13px, text-secondary): «Настройки применяются ко всем новым событиям во всех пространствах. Уже созданные напоминания не изменятся.» Toggle SHALL вызывать API `PUT /api/user/reminders` при переключении. При ошибке SHALL откатывать состояние toggle.

#### Scenario: Переключение напоминания
- **WHEN** пользователь включает toggle «За 1 час»
- **THEN** API вызывается с `{"1h": true}`, toggle отображается включённым

#### Scenario: Ошибка сохранения
- **WHEN** API возвращает ошибку при переключении
- **THEN** toggle возвращается в предыдущее состояние

### Requirement: Удаление зависимости @telegram-apps/telegram-ui
Проект SHALL НЕ импортировать и НЕ использовать пакет `@telegram-apps/telegram-ui`. Все UI-компоненты (Section, Cell, Button, Input, Switch, List, Badge, Spinner, Placeholder) SHALL быть заменены на кастомные компоненты из miniapp-ui-components. Пакет SHALL быть удалён из `package.json`.

#### Scenario: Сборка без @telegram-apps/telegram-ui
- **WHEN** проект собирается (`npm run build`)
- **THEN** сборка проходит успешно без пакета `@telegram-apps/telegram-ui`

## ADDED Requirements

### Requirement: Loading и Error состояния без Telegram UI
Система SHALL предоставлять компоненты LoadingView (спиннер + текст «Загрузка...»), ErrorView (текст ошибки + кнопка «Повторить»), EmptyView (текст сообщения) без использования Telegram UI Spinner/Placeholder. Компоненты SHALL использовать кастомные стили из дизайн-системы.

#### Scenario: Состояние загрузки
- **WHEN** данные загружаются
- **THEN** отображается анимированный спиннер и текст «Загрузка...» по центру

#### Scenario: Состояние ошибки с повтором
- **WHEN** загрузка завершилась ошибкой
- **THEN** отображается текст ошибки и кнопка «Повторить»
