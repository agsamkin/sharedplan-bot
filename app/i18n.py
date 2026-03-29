"""Модуль интернационализации (i18n) для бота.

Содержит словари переводов для ru и en.
Функция t(lang, key, **kwargs) возвращает локализованную строку.
"""

from __future__ import annotations

SUPPORTED_LANGUAGES = ("ru", "en")
DEFAULT_LANGUAGE = "en"


def normalize_language(lang: str | None) -> str:
    """Нормализовать код языка в поддерживаемый."""
    if lang and lang.startswith("ru"):
        return "ru"
    return "en"


MESSAGES_RU: dict[str, str] = {
    # ── start.py ──
    "start.welcome.intro": (
        "Привет! Я помогу организовать совместные планы.\n\n"
        "Что я умею:\n"
        "📅 Создавать события из текста или голосовых сообщений\n"
        "👥 Объединять участников в пространства с общим календарём\n"
        "🔔 Отправлять персональные напоминания\n"
    ),
    "start.welcome.spaces": "\nТвои пространства: {names}\n",
    "start.welcome.has_spaces": "\nОтправь текст или голосовое, чтобы создать событие.",
    "start.welcome.no_spaces": "\nОткрой приложение, чтобы создать первое пространство.",
    "start.open_app": "📱 Открыть приложение",
    "start.join.invalid_link": "Ссылка недействительна или пространство удалено.",
    "start.join.already_member": "Ты уже состоишь в пространстве «{name}».",
    "start.join.success": "Ты присоединился к пространству «{name}»!",
    "start.join.notification": "👋 {joiner} присоединился к «{space}»!",

    # ── help.py ──
    "help.text": (
        "📅 Создание событий\n"
        "Просто напиши или надиктуй событие — я распознаю дату и время.\n"
        "Например: «Ужин завтра в 19:00» или «День рождения Ани 5 апреля».\n\n"
        "📱 Управление\n"
        "Пространства, события и напоминания — в приложении.\n"
        "Нажми кнопку меню слева от поля ввода.\n\n"
        "Команды:\n"
        "/help — Эта справка\n"
        "/privacy — Политика конфиденциальности"
    ),

    # ── privacy.py ──
    "privacy.text": "🔒 Политика конфиденциальности:\nhttps://telegram.org/privacy",

    # ── event.py ──
    "event.no_spaces": "У тебя пока нет пространств. Создай первое через /newspace!",
    "event.too_long": "❌ Слишком длинное сообщение. Опиши событие короче (до {max_len} символов).",
    "event.select_space": "В какое пространство добавить событие?",
    "event.past_date_warning": "⚠️ Дата уже прошла ({date}).\n\n📝 {title}\n\nВсё равно создать?",
    "event.open_app": "Открыть приложение",

    # ── voice.py ──
    "voice.too_long": "❌ Слишком длинное голосовое сообщение ({duration} сек). Максимум — {max_duration} сек.",
    "voice.too_large": "❌ Слишком большой аудиофайл. Попробуй записать сообщение короче.",
    "voice.transcript_too_long": (
        "🎤 Распознано: «{transcript}»\n\n"
        "❌ Слишком длинное сообщение. Опиши событие короче (до {max_len} символов)."
    ),

    # ── formatting.py ──
    "fmt.months.1": "января", "fmt.months.2": "февраля", "fmt.months.3": "марта",
    "fmt.months.4": "апреля", "fmt.months.5": "мая", "fmt.months.6": "июня",
    "fmt.months.7": "июля", "fmt.months.8": "августа", "fmt.months.9": "сентября",
    "fmt.months.10": "октября", "fmt.months.11": "ноября", "fmt.months.12": "декабря",

    "fmt.weekdays.0": "понедельник", "fmt.weekdays.1": "вторник", "fmt.weekdays.2": "среда",
    "fmt.weekdays.3": "четверг", "fmt.weekdays.4": "пятница", "fmt.weekdays.5": "суббота",
    "fmt.weekdays.6": "воскресенье",

    "fmt.weekdays_acc.0": "в понедельник", "fmt.weekdays_acc.1": "во вторник",
    "fmt.weekdays_acc.2": "в среду", "fmt.weekdays_acc.3": "в четверг",
    "fmt.weekdays_acc.4": "в пятницу", "fmt.weekdays_acc.5": "в субботу",
    "fmt.weekdays_acc.6": "в воскресенье",

    "fmt.relative.today": "сегодня", "fmt.relative.tomorrow": "завтра",
    "fmt.relative.day_after": "послезавтра",

    "fmt.conflict_warning": "⚠️ На близкое время уже есть события:",
    "fmt.confirmation.transcript": "🎤 Распознано: «{transcript}»\n",
    "fmt.confirmation.header": "📌 Событие:",
    "fmt.confirmation.publish": "\nОпубликовать?",

    "fmt.notification.new_event": "📅 Новое событие в «{space}»!\n",
    "fmt.notification.added_by": "👤 Добавил: {name}",

    "fmt.manage.header": "⚙️ Управление событием:\n",

    "fmt.edited.header": "✏️ Событие изменено в «{space}»!\n",
    "fmt.edited.changed_by": "👤 Изменил: {name}",

    "fmt.deleted.header": "🗑 Событие удалено в «{space}»!\n",
    "fmt.deleted.deleted_by": "👤 Удалил: {name}",

    "fmt.space_deleted": (
        "🗑 Пространство «{name}» удалено\n\n"
        "👤 Удалил: {admin}\n"
        "ℹ️ Напоминания из этого пространства больше не будут приходить."
    ),

    # ── keyboards/confirm.py ──
    "kb.confirm.yes": "✅ Да",
    "kb.confirm.edit": "✏️ Изменить",
    "kb.confirm.cancel": "❌ Отмена",
    "kb.confirm.past_confirm": "✅ Всё равно создать",
    "kb.confirm.past_cancel": "❌ Отмена",
    "kb.confirm.delete_yes": "Да, удалить",
    "kb.confirm.delete_cancel": "Отмена",

    # ── callbacks/event_confirm.py ──
    "cb.confirm.no_data": "Нет данных события",
    "cb.confirm.published": "✅ Событие опубликовано!",
    "cb.confirm.cancelled": "❌ Создание события отменено.",
    "cb.confirm.edit_prompt": "Отправь исправленный вариант.",

    # ── callbacks/space_select.py ──
    "cb.space.unknown_action": "Неизвестное действие",
    "cb.space.use_app": "Это действие доступно в приложении",

    # ── middlewares/access_control.py ──
    "access.private_bot": "Этот бот доступен только по приглашению. Попроси ссылку у владельца.",
    "access.denied": "Доступ запрещён",
    "access.error": "Произошла ошибка. Попробуй позже.",
    "access.error_short": "Произошла ошибка",

    # ── parse errors ──
    "parse_error.invalid_json": "Не удалось распознать событие. Попробуй описать его проще, например: «Ужин завтра в 19:00».",
    "parse_error.timeout": "Не удалось связаться с сервисом. Попробуй ещё раз через пару секунд.",
    "parse_error.network": "Не удалось связаться с сервисом. Попробуй ещё раз через пару секунд.",
    "parse_error.rate_limit": "Сервис временно перегружен. Попробуй через минуту.",
    "parse_error.service_disabled": "Автоматическое распознавание событий отключено. Создай событие вручную в приложении.",

    # ── STT errors ──
    "stt_error.timeout": "Не удалось распознать голосовое сообщение. Попробуй записать ещё раз или напиши текстом.",
    "stt_error.service_unavailable": "Не удалось распознать голосовое сообщение. Попробуй записать ещё раз или напиши текстом.",
    "stt_error.empty_result": "Не удалось разобрать речь — возможно, запись слишком тихая. Попробуй записать ещё раз или напиши текстом.",
    "stt_error.auth_error": "Сервис распознавания речи временно недоступен. Попробуй позже или напиши текстом.",
    "stt_error.bad_request": "Не удалось распознать голосовое сообщение. Попробуй записать ещё раз или напиши текстом.",
    "stt_error.service_disabled": "Функция голосовых сообщений отключена. Напиши текстом или создай событие в приложении.",

    # ── reminder labels ──
    "reminder.label.1d": "За 1 день",
    "reminder.label.2h": "За 2 часа",
    "reminder.label.1h": "За 1 час",
    "reminder.label.30m": "За 30 минут",
    "reminder.label.15m": "За 15 минут",
    "reminder.label.0m": "В момент события",

    # ── reminder relative labels ──
    "reminder.relative.1d": "Завтра",
    "reminder.relative.2h": "Через 2 часа",
    "reminder.relative.1h": "Через 1 час",
    "reminder.relative.30m": "Через 30 минут",
    "reminder.relative.15m": "Через 15 минут",
    "reminder.relative.0m": "Сейчас",

    # ── reminder message ──
    "reminder.message.header": "🔔 Напоминание!\n",
    "reminder.message.space": "📍 Пространство: {name}",

    # ── reminders command ──
    "reminders.go_to_app": "Настрой напоминания в приложении:",
    "reminders.button": "⏰ Настройки напоминаний",

    # ── recurrence labels ──
    "recurrence.daily": "Каждый день",
    "recurrence.weekly": "Каждую неделю",
    "recurrence.biweekly": "Каждые 2 недели",
    "recurrence.monthly": "Каждый месяц",
    "recurrence.yearly": "Каждый год",
}


MESSAGES_EN: dict[str, str] = {
    # ── start.py ──
    "start.welcome.intro": (
        "Hi! I'll help you organize shared plans.\n\n"
        "What I can do:\n"
        "📅 Create events from text or voice messages\n"
        "👥 Unite members in spaces with shared calendars\n"
        "🔔 Send personalized reminders\n"
    ),
    "start.welcome.spaces": "\nYour spaces: {names}\n",
    "start.welcome.has_spaces": "\nSend text or voice message to create an event.",
    "start.welcome.no_spaces": "\nOpen the app to create your first space.",
    "start.open_app": "📱 Open app",
    "start.join.invalid_link": "The link is invalid or the space has been deleted.",
    "start.join.already_member": "You are already a member of \"{name}\".",
    "start.join.success": "You joined \"{name}\"!",
    "start.join.notification": "👋 {joiner} joined \"{space}\"!",

    # ── help.py ──
    "help.text": (
        "📅 Creating events\n"
        "Just type or dictate an event — I'll recognize the date and time.\n"
        "For example: \"Dinner tomorrow at 7 PM\" or \"Ann's birthday on April 5\".\n\n"
        "📱 Management\n"
        "Spaces, events and reminders — in the app.\n"
        "Tap the menu button to the left of the input field.\n\n"
        "Commands:\n"
        "/help — This help\n"
        "/privacy — Privacy policy"
    ),

    # ── privacy.py ──
    "privacy.text": "🔒 Privacy policy:\nhttps://telegram.org/privacy",

    # ── event.py ──
    "event.no_spaces": "You don't have any spaces yet. Create one via /newspace!",
    "event.too_long": "❌ Message is too long. Keep it under {max_len} characters.",
    "event.select_space": "Which space should the event go to?",
    "event.past_date_warning": "⚠️ The date has already passed ({date}).\n\n📝 {title}\n\nCreate anyway?",
    "event.open_app": "Open app",

    # ── voice.py ──
    "voice.too_long": "❌ Voice message is too long ({duration} sec). Maximum is {max_duration} sec.",
    "voice.too_large": "❌ Audio file is too large. Try recording a shorter message.",
    "voice.transcript_too_long": (
        "🎤 Recognized: \"{transcript}\"\n\n"
        "❌ Message is too long. Keep it under {max_len} characters."
    ),

    # ── formatting.py ──
    "fmt.months.1": "January", "fmt.months.2": "February", "fmt.months.3": "March",
    "fmt.months.4": "April", "fmt.months.5": "May", "fmt.months.6": "June",
    "fmt.months.7": "July", "fmt.months.8": "August", "fmt.months.9": "September",
    "fmt.months.10": "October", "fmt.months.11": "November", "fmt.months.12": "December",

    "fmt.weekdays.0": "Monday", "fmt.weekdays.1": "Tuesday", "fmt.weekdays.2": "Wednesday",
    "fmt.weekdays.3": "Thursday", "fmt.weekdays.4": "Friday", "fmt.weekdays.5": "Saturday",
    "fmt.weekdays.6": "Sunday",

    "fmt.weekdays_acc.0": "on Monday", "fmt.weekdays_acc.1": "on Tuesday",
    "fmt.weekdays_acc.2": "on Wednesday", "fmt.weekdays_acc.3": "on Thursday",
    "fmt.weekdays_acc.4": "on Friday", "fmt.weekdays_acc.5": "on Saturday",
    "fmt.weekdays_acc.6": "on Sunday",

    "fmt.relative.today": "today", "fmt.relative.tomorrow": "tomorrow",
    "fmt.relative.day_after": "day after tomorrow",

    "fmt.conflict_warning": "⚠️ There are events at a similar time:",
    "fmt.confirmation.transcript": "🎤 Recognized: \"{transcript}\"\n",
    "fmt.confirmation.header": "📌 Event:",
    "fmt.confirmation.publish": "\nPublish?",

    "fmt.notification.new_event": "📅 New event in \"{space}\"!\n",
    "fmt.notification.added_by": "👤 Added by: {name}",

    "fmt.manage.header": "⚙️ Manage event:\n",

    "fmt.edited.header": "✏️ Event changed in \"{space}\"!\n",
    "fmt.edited.changed_by": "👤 Changed by: {name}",

    "fmt.deleted.header": "🗑 Event deleted in \"{space}\"!\n",
    "fmt.deleted.deleted_by": "👤 Deleted by: {name}",

    "fmt.space_deleted": (
        "🗑 Space \"{name}\" deleted\n\n"
        "👤 Deleted by: {admin}\n"
        "ℹ️ Reminders from this space will no longer be sent."
    ),

    # ── keyboards/confirm.py ──
    "kb.confirm.yes": "✅ Yes",
    "kb.confirm.edit": "✏️ Edit",
    "kb.confirm.cancel": "❌ Cancel",
    "kb.confirm.past_confirm": "✅ Create anyway",
    "kb.confirm.past_cancel": "❌ Cancel",
    "kb.confirm.delete_yes": "Yes, delete",
    "kb.confirm.delete_cancel": "Cancel",

    # ── callbacks/event_confirm.py ──
    "cb.confirm.no_data": "No event data",
    "cb.confirm.published": "✅ Event published!",
    "cb.confirm.cancelled": "❌ Event creation cancelled.",
    "cb.confirm.edit_prompt": "Send the corrected version.",

    # ── callbacks/space_select.py ──
    "cb.space.unknown_action": "Unknown action",
    "cb.space.use_app": "This action is available in the app",

    # ── middlewares/access_control.py ──
    "access.private_bot": "This bot is invite-only. Ask the owner for a link.",
    "access.denied": "Access denied",
    "access.error": "An error occurred. Try again later.",
    "access.error_short": "An error occurred",

    # ── parse errors ──
    "parse_error.invalid_json": "Couldn't recognize the event. Try describing it more simply, e.g.: \"Dinner tomorrow at 7 PM\".",
    "parse_error.timeout": "Couldn't reach the service. Try again in a few seconds.",
    "parse_error.network": "Couldn't reach the service. Try again in a few seconds.",
    "parse_error.rate_limit": "Service is temporarily overloaded. Try again in a minute.",
    "parse_error.service_disabled": "Automatic event recognition is disabled. Create an event manually in the app.",

    # ── STT errors ──
    "stt_error.timeout": "Couldn't recognize the voice message. Try recording again or type it out.",
    "stt_error.service_unavailable": "Couldn't recognize the voice message. Try recording again or type it out.",
    "stt_error.empty_result": "Couldn't understand the speech — maybe the recording is too quiet. Try again or type it out.",
    "stt_error.auth_error": "Speech recognition service is temporarily unavailable. Try later or type it out.",
    "stt_error.bad_request": "Couldn't recognize the voice message. Try recording again or type it out.",
    "stt_error.service_disabled": "Voice messages are disabled. Type it out or create an event in the app.",

    # ── reminder labels ──
    "reminder.label.1d": "1 day before",
    "reminder.label.2h": "2 hours before",
    "reminder.label.1h": "1 hour before",
    "reminder.label.30m": "30 min before",
    "reminder.label.15m": "15 min before",
    "reminder.label.0m": "At the time of event",

    # ── reminder relative labels ──
    "reminder.relative.1d": "Tomorrow",
    "reminder.relative.2h": "In 2 hours",
    "reminder.relative.1h": "In 1 hour",
    "reminder.relative.30m": "In 30 minutes",
    "reminder.relative.15m": "In 15 minutes",
    "reminder.relative.0m": "Now",

    # ── reminder message ──
    "reminder.message.header": "🔔 Reminder!\n",
    "reminder.message.space": "📍 Space: {name}",

    # ── reminders command ──
    "reminders.go_to_app": "Set up reminders in the app:",
    "reminders.button": "⏰ Reminder settings",

    # ── recurrence labels ──
    "recurrence.daily": "Every day",
    "recurrence.weekly": "Every week",
    "recurrence.biweekly": "Every 2 weeks",
    "recurrence.monthly": "Every month",
    "recurrence.yearly": "Every year",
}


_MESSAGES = {
    "ru": MESSAGES_RU,
    "en": MESSAGES_EN,
}


def t(lang: str, key: str, **kwargs: object) -> str:
    """Получить локализованную строку.

    Возвращает сам ключ как fallback при отсутствии перевода.
    """
    messages = _MESSAGES.get(lang, _MESSAGES["en"])
    template = messages.get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template


def get_reminder_labels(lang: str) -> dict[str, str]:
    """Получить локализованные метки интервалов напоминаний."""
    return {
        key: t(lang, f"reminder.label.{key}")
        for key in ("1d", "2h", "1h", "30m", "15m", "0m")
    }


def get_relative_labels(lang: str) -> dict[str, str]:
    """Получить локализованные относительные метки напоминаний."""
    return {
        key: t(lang, f"reminder.relative.{key}")
        for key in ("1d", "2h", "1h", "30m", "15m", "0m")
    }


def get_recurrence_label(lang: str, rule: str | None) -> str | None:
    """Получить локализованную метку повторения."""
    if rule is None:
        return None
    return t(lang, f"recurrence.{rule}")
