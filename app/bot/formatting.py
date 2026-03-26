from datetime import date, time

MONTHS = [
    "", "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]

FORMAT_HINT = "Формат: название, ДД.ММ.ГГГГ, ЧЧ:ММ\nВремя можно не указывать."


def format_date_human(d: date) -> str:
    """Дата в формате «27 марта 2026»."""
    return f"{d.day} {MONTHS[d.month]} {d.year}"


def format_date_relative(d: date) -> str:
    """Дата с относительными значениями: сегодня/завтра или «5 апреля»."""
    delta = (d - date.today()).days
    if delta == 0:
        return "сегодня"
    if delta == 1:
        return "завтра"
    return f"{d.day} {MONTHS[d.month]}"


def format_confirmation(title: str, event_date: date, event_time: time | None) -> str:
    """Карточка подтверждения события."""
    lines = [
        "📌 Событие:",
        f"📝 {title}",
        f"📅 {format_date_human(event_date)}",
    ]
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
        f"📅 {format_date_human(event_date)}",
    ]
    if event_time is not None:
        lines.append(f"⏰ {event_time.strftime('%H:%M')}")
    lines.append(f"👤 Добавил: {creator_name}")
    return "\n".join(lines)
