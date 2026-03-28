## 1. Дизайн-система и базовые компоненты

- [x] 1.1 Создать файл CSS-переменных дизайн-системы (light/dark темы) и подключить определение темы через `colorScheme`
- [x] 1.2 Создать SVG-иконки как React-компоненты (`components/icons/`): ChevronRight, IconCalendar, IconClock, IconPeople, IconBell, IconLink, IconTrash, IconEdit, IconBack, IconPerson, IconCheck
- [x] 1.3 Создать компонент Avatar (инициалы, цветовая кодировка по ID, настраиваемый размер)
- [x] 1.4 Создать компоненты Section и Divider
- [x] 1.5 Создать компонент ListItem (left/title/subtitle/right, danger, compact)
- [x] 1.6 Создать компонент Header (sticky, кнопка назад, правый элемент)
- [x] 1.7 Создать компонент Toggle (iOS-стиль, анимация 200ms)
- [x] 1.8 Создать компонент ActionButton (иконка + подпись, настраиваемый цвет)
- [x] 1.9 Создать компонент Toast (fadeInUp, auto-dismiss 2с)
- [x] 1.10 Создать компонент DateBadge (число + месяц)
- [x] 1.11 Создать компонент ConfirmInline (инлайн-блок подтверждения удаления)
- [x] 1.12 Переписать LoadingView, ErrorView, EmptyView без Telegram UI

## 2. Обновление App и навигации

- [x] 2.1 Удалить импорт `@telegram-apps/telegram-ui` и `AppRoot` из App.tsx
- [x] 2.2 Обновить маршруты: добавить `/spaces/:id/edit`, `/spaces/:id/members`, заменить `/events/:id/edit` на `/events/:id`, убрать `/spaces/:id/settings`
- [x] 2.3 Обновить BackButtonHandler для новых маршрутов
- [x] 2.4 Подключить провайдер Toast (контекст или глобальное состояние)
- [x] 2.5 Применить CSS-переменные дизайн-системы на корневой элемент

## 3. Экран «Пространства» (SpacesPage)

- [x] 3.1 Переписать SpacesPage на кастомные компоненты: Section, ListItem, Avatar, Divider
- [x] 3.2 Добавить секцию «Настройки» с ListItem «Напоминания» (IconBell, подпись)
- [x] 3.3 Обновить empty/loading/error состояния на новые компоненты

## 4. Экран «Детали пространства» (SpaceDetailPage)

- [x] 4.1 Создать SpaceDetailPage: загрузка данных пространства и событий через API
- [x] 4.2 Реализовать панель action-кнопок (Изменить, Участники, Ссылка, Удалить) с учётом роли пользователя
- [x] 4.3 Реализовать список событий с DateBadge, относительными датами и навигацией к EventDetail
- [x] 4.4 Реализовать инлайн-подтверждение удаления пространства с вызовом API
- [x] 4.5 Реализовать копирование invite-ссылки с Toast

## 5. Экран «Редактирование пространства» (SpaceEditPage)

- [x] 5.1 Создать SpaceEditPage: input с названием (autoFocus), кнопка «Сохранить» (disabled если пусто)
- [x] 5.2 Подключить API обновления названия пространства (потребуется новый или существующий endpoint) и Toast

## 6. Экран «Участники» (MembersPage)

- [x] 6.1 Создать MembersPage: список участников с Avatar, ролевыми бейджами (admin badge)
- [x] 6.2 Реализовать кнопку «Удалить» для не-админов (только для администратора) с инлайн-подтверждением
- [x] 6.3 Добавить подпись «Новые участники присоединяются по invite-ссылке пространства»

## 7. Экран «Детали события» (EventDetailPage)

- [x] 7.1 Переписать EventEditPage → EventDetailPage: Section «Детали события» с полями Название, Дата, Время
- [x] 7.2 Добавить Section с информацией об авторе (IconPerson + имя)
- [x] 7.3 Реализовать кнопку «Сохранить» с вызовом API и Toast
- [x] 7.4 Реализовать кнопку «Удалить событие» с инлайн-подтверждением и Toast

## 8. Экран «Напоминания» (ReminderSettingsPage)

- [x] 8.1 Переписать ReminderSettingsPage на кастомные компоненты: Section, Toggle, divider
- [x] 8.2 Добавить подпись под секцией про область действия настроек

## 9. Очистка и финализация

- [x] 9.1 Удалить `@telegram-apps/telegram-ui` из package.json и `@telegram-apps/telegram-ui/dist/styles.css` из импортов
- [x] 9.2 Удалить неиспользуемые файлы: старый ConfirmDialog.tsx (заменён на ConfirmInline), SpaceSettingsPage.tsx
- [x] 9.3 Убедиться что `npm run build` проходит без ошибок
- [x] 9.4 Проверить dark mode: все CSS-переменные корректно переключаются
- [x] 9.5 Проверить все touch targets >= 44px, контраст текста >= 4.5:1
