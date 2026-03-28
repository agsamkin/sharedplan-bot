from datetime import date, time

MONTHS = [
    "", "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]

# Именительный падеж — для карточки подтверждения («28 марта 2026, суббота»)
WEEKDAYS_NOMINATIVE = [
    "понедельник", "вторник", "среда", "четверг",
    "пятница", "суббота", "воскресенье",
]

# Винительный падеж — для относительных дат («в среду», «в пятницу»)
WEEKDAYS_ACCUSATIVE = [
    "в понедельник", "во вторник", "в среду", "в четверг",
    "в пятницу", "в субботу", "в воскресенье",
]

PARSE_ERROR_MESSAGES = {
    "invalid_json": (
        "Не удалось распознать событие. "
        "Попробуй описать его проще, например: «Ужин завтра в 19:00»."
    ),
    "timeout": "Не удалось связаться с сервисом. Попробуй ещё раз через пару секунд.",
    "network": "Не удалось связаться с сервисом. Попробуй ещё раз через пару секунд.",
    "rate_limit": "Сервис временно перегружен. Попробуй через минуту.",
}

STT_ERROR_MESSAGES = {
    "timeout": "Не удалось распознать голосовое сообщение. Попробуй записать ещё раз или напиши текстом.",
    "service_unavailable": "Не удалось распознать голосовое сообщение. Попробуй записать ещё раз или напиши текстом.",
    "empty_result": "Не удалось разобрать речь — возможно, запись слишком тихая. Попробуй записать ещё раз или напиши текстом.",
    "auth_error": "Сервис распознавания речи временно недоступен. Попробуй позже или напиши текстом.",
    "bad_request": "Не удалось распознать голосовое сообщение. Попробуй записать ещё раз или напиши текстом.",
}

def format_date_human(d: date) -> str:
    """Дата в формате «27 марта 2026»."""
    return f"{d.day} {MONTHS[d.month]} {d.year}"


def format_date_with_weekday(d: date) -> str:
    """Дата с днём недели: «28 марта 2026, суббота»."""
    weekday = WEEKDAYS_NOMINATIVE[d.weekday()]
    return f"{d.day} {MONTHS[d.month]} {d.year}, {weekday}"


def format_date_relative(d: date) -> str:
    """Расширенные относительные даты: сегодня/завтра/послезавтра/день недели или «5 апреля»."""
    delta = (d - date.today()).days
    if delta == 0:
        return "сегодня"
    if delta == 1:
        return "завтра"
    if delta == 2:
        return "послезавтра"
    if 3 <= delta <= 6:
        return WEEKDAYS_ACCUSATIVE[d.weekday()]
    return f"{d.day} {MONTHS[d.month]}"


def format_date_short_with_weekday(d: date) -> str:
    """Короткая дата с днём недели: «28 марта, суббота»."""
    weekday = WEEKDAYS_NOMINATIVE[d.weekday()]
    return f"{d.day} {MONTHS[d.month]}, {weekday}"


def format_confirmation(
    title: str, event_date: date, event_time: time | None, transcript: str | None = None,
) -> str:
    """Карточка подтверждения события."""
    lines = []
    if transcript:
        lines.append(f"🎤 Распознано: «{transcript}»\n")
    lines.append("📌 Событие:")
    lines.append(f"📝 {title}")
    lines.append(f"📅 {format_date_with_weekday(event_date)}")
    if event_time is not None:
        lines.append(f"⏰ {event_time.strftime('%H:%M')}")
    lines.append("\nОпубликовать?")
    return "\n".join(lines)


def format_notification(
    space_name: str, title: str, event_date: date, event_time: time | None, creator_name: str,
) -> str:
    """Уведомление участников о новом событии."""
    lines = [
        f"📅 Новое событие в «{space_name}»!\n",
        f"📝 {title}",
        f"📅 {format_date_relative(event_date).capitalize()}",
    ]
    if event_time is not None:
        lines.append(f"⏰ {event_time.strftime('%H:%M')}")
    lines.append(f"👤 Добавил: {creator_name}")
    return "\n".join(lines)


def format_event_manage_card(
    title: str, event_date: date, event_time: time | None,
) -> str:
    """Карточка управления событием."""
    lines = [
        "⚙️ Управление событием:\n",
        f"📝 {title}",
        f"📅 {format_date_with_weekday(event_date)}",
    ]
    if event_time is not None:
        lines.append(f"⏰ {event_time.strftime('%H:%M')}")
    return "\n".join(lines)


def format_event_edited_notification(
    space_name: str, title: str, field_label: str,
    old_value: str, new_value: str, editor_name: str,
) -> str:
    """Уведомление участников об изменении события."""
    lines = [
        f"✏️ Событие изменено в «{space_name}»!\n",
        f"📝 {title}",
        f"🔄 {field_label}: {old_value} → {new_value}",
        f"👤 Изменил: {editor_name}",
    ]
    return "\n".join(lines)


def format_event_deleted_notification(
    space_name: str, title: str, editor_name: str,
) -> str:
    """Уведомление участников об удалении события."""
    lines = [
        f"🗑 Событие удалено в «{space_name}»!\n",
        f"📝 {title}",
        f"👤 Удалил: {editor_name}",
    ]
    return "\n".join(lines)
