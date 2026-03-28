## Context

Текущий Mini App построен на `@telegram-apps/telegram-ui` — библиотеке стандартных компонентов Telegram. Это обеспечило быстрый запуск, но результат выглядит шаблонно: нет визуальной иерархии событий, нет аватаров, нет инлайн-подтверждений, нет тостов. Подготовлен JSX-макет (`docs/shared-plan-miniapp.jsx`) с iOS-стилем интерфейса, на который нужно перевести фронтенд.

**Текущий стек фронтенда:**
- React 18.2 + TypeScript + Vite 6
- `@telegram-apps/telegram-ui` (Section, Cell, Button, Input, Switch, Spinner, Placeholder)
- `@telegram-apps/sdk-react` (инициализация, initData)
- React Router v7 (BrowserRouter, Routes)
- Inline styles + Telegram CSS-переменные

**Текущие экраны:**
- SpacesPage (`/`) — список пространств
- SpaceEventsPage (`/spaces/:id`) — события пространства
- SpaceSettingsPage (`/spaces/:id/settings`) — настройки + участники + удаление
- EventEditPage (`/events/:id/edit`) — редактирование события
- ReminderSettingsPage (`/settings/reminders`) — тогглы напоминаний

## Goals / Non-Goals

**Goals:**
- Реализовать все экраны в соответствии с JSX-макетом
- Создать библиотеку переиспользуемых UI-компонентов (Header, ListItem, Avatar, Section, Toggle, ActionButton, Toast и др.)
- Убрать зависимость от `@telegram-apps/telegram-ui`
- Обеспечить поддержку Telegram dark/light theme через собственные CSS-переменные
- Соблюдать UI/UX Pro Max стандарты: touch targets 44×44px, контраст 4.5:1, SVG-иконки, 8dp spacing, анимации 150–300ms

**Non-Goals:**
- ~~Изменение backend API~~ — добавлен `PUT /api/spaces/:id` для переименования пространства, т.к. новый экран SpaceEdit требует этого эндпоинта (обоснованное отклонение)
- Добавление новой функциональности (только UI-переработка)
- Отказ от React Router (сохраняем, но меняем маршруты)
- Оффлайн-режим и PWA

## Decisions

### 1. Кастомные компоненты вместо Telegram UI

**Решение:** заменить `@telegram-apps/telegram-ui` на собственные компоненты, повторяющие макет.

**Альтернатива:** оставить Telegram UI и кастомизировать через CSS overrides — отвергнуто, т.к. библиотека ограничивает layout (нет action-кнопок, нет инлайн-подтверждений, нет date-badges).

**Компоненты:**
- `Header` — sticky-заголовок с кнопкой назад и опциональным правым элементом
- `ListItem` — универсальная строка (left/title/subtitle/right), поддержка compact и danger
- `Avatar` — круг с инициалами и цветовой кодировкой по ID
- `Section` — группировка с опциональным заголовком
- `Divider` — разделитель с отступом слева (70px)
- `Toggle` — iOS-стилевой переключатель (48×28, зелёный/серый)
- `ActionButton` — кнопка-действие (иконка + подпись), используется на Space Detail
- `Toast` — всплывающее уведомление снизу с fadeInUp-анимацией
- `ConfirmInline` — инлайн-блок подтверждения удаления (заменяет модальный диалог)
- `DateBadge` — плашка с числом и месяцем для списка событий
- `IconButton` — кнопка с SVG-иконкой

### 2. Маршруты

**Решение:** сохранить React Router, обновить маршруты под новую структуру экранов.

| Экран | Маршрут | Текущий |
|-------|---------|---------|
| Пространства | `/` | `/` (без изменений) |
| Детали пространства | `/spaces/:id` | `/spaces/:id` (был SpaceEventsPage, теперь SpaceDetailPage) |
| Редактирование пространства | `/spaces/:id/edit` | нет (новый) |
| Участники | `/spaces/:id/members` | часть SpaceSettingsPage |
| Детали/редактирование события | `/events/:id` | `/events/:id/edit` |
| Напоминания | `/settings/reminders` | `/settings/reminders` (без изменений) |

**Убираемый маршрут:** `/spaces/:id/settings` — функционал распределён между Space Detail, Space Edit и Members.

### 3. Дизайн-система и темизация

**Решение:** собственные CSS-переменные, привязанные к Telegram `colorScheme`.

**Палитра (light):**
| Токен | Значение | Назначение |
|-------|----------|------------|
| `--bg-primary` | `#f2f2f7` | Фон экранов |
| `--bg-card` | `#ffffff` | Фон секций/карточек |
| `--text-primary` | `#1a1a1a` | Основной текст |
| `--text-secondary` | `#8e8e93` | Подписи, хинты |
| `--accent-blue` | `#378ADD` | Ссылки, кнопка «назад», primary CTA |
| `--accent-green` | `#1D9E75` | Toggle on, успех |
| `--accent-red` | `#E24B4A` | Удаление, danger |
| `--accent-purple` | `#7F77DD` | Бейдж admin, действие «ссылка» |
| `--border` | `#e5e5e5` | Разделители, бордеры |
| `--border-input` | `#d1d1d6` | Бордер инпутов |

**Dark mode:** инвертированные значения, привязка через `[data-theme="dark"]` selector или Telegram CSS variable fallback.

**Типографика:** системный `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`:
- Заголовок экрана: 17px / 600
- Заголовок секции: 12px / 600 / uppercase / letter-spacing 0.8
- ListItem title: 15px / 500
- ListItem subtitle: 13px / 400
- Кнопка action: 11px / 500
- Toast: 14px / 500

**Spacing:** 4/8/12/16/20/24/32px (кратно 4).

### 4. SVG-иконки

**Решение:** inline SVG-компоненты (как в макете), без внешних icon-библиотек.

Набор иконок: ChevronRight, IconCalendar, IconClock, IconPeople, IconBell, IconLink, IconTrash, IconEdit, IconBack, IconPerson, IconCheck.

**Альтернатива:** Lucide React — отвергнуто, т.к. макет уже содержит готовые SVG, и внешняя зависимость не нужна.

### 5. Аватары

**Решение:** компонент Avatar с инициалами из имени и детерминированным цветом по `user_id % 7`.

Палитра аватаров: `["#7F77DD", "#1D9E75", "#D85A30", "#D4537E", "#378ADD", "#639922", "#BA7517"]`.

### 6. Toast вместо модальных диалогов для успеха

**Решение:** Toast (auto-dismiss 2с) для операций «сохранено», «удалено», «ссылка скопирована». Inline-подтверждение для деструктивных действий (удаление пространства/события/участника).

**Альтернатива:** модальные диалоги (текущая реализация) — отвергнуто, т.к. инлайн-подтверждения в контексте экрана менее прерывают flow пользователя.

### 7. Сохранение `@telegram-apps/sdk-react`

**Решение:** оставить для инициализации WebApp (ready(), expand(), initData, BackButton, colorScheme). Убрать только `@telegram-apps/telegram-ui`.

## Risks / Trade-offs

- **[Объём изменений]** → Полная переработка фронтенда. Mitigation: Backend без изменений, API стабилен, можно тестировать экран за экраном.
- **[Dark mode]** → Собственная темизация сложнее, чем Telegram UI. Mitigation: минимальный набор токенов (10 переменных), тестирование в обоих режимах.
- **[Telegram UI обновления]** → Теряем автоматические обновления стиля Telegram. Mitigation: макет уже использует нейтральный iOS-стиль, визуально совместимый с Telegram.
- **[Размер бандла]** → Inline SVG увеличивают размер JSX. Mitigation: SVG минимальные (14–18px viewBox), общий вклад ~2KB.
