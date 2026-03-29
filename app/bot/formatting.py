from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from app.i18n import t

if TYPE_CHECKING:
    from app.db.models import Event


def _month(lang: str, month: int) -> str:
    return t(lang, f"fmt.months.{month}")


def _weekday_nom(lang: str, wd: int) -> str:
    return t(lang, f"fmt.weekdays.{wd}")


def _weekday_acc(lang: str, wd: int) -> str:
    return t(lang, f"fmt.weekdays_acc.{wd}")


def get_parse_error_message(lang: str, error_type: str) -> str:
    return t(lang, f"parse_error.{error_type}")


def get_stt_error_message(lang: str, error_type: str) -> str:
    return t(lang, f"stt_error.{error_type}")


def format_date_human(d: date, lang: str = "ru") -> str:
    """Дата в формате «27 марта 2026» / «27 March 2026»."""
    return f"{d.day} {_month(lang, d.month)} {d.year}"


def format_date_with_weekday(d: date, lang: str = "ru") -> str:
    """Дата с днём недели: «28 марта 2026, суббота»."""
    weekday = _weekday_nom(lang, d.weekday())
    return f"{d.day} {_month(lang, d.month)} {d.year}, {weekday}"


def format_date_relative(d: date, lang: str = "ru") -> str:
    """Расширенные относительные даты."""
    delta = (d - date.today()).days
    if delta == 0:
        return t(lang, "fmt.relative.today")
    if delta == 1:
        return t(lang, "fmt.relative.tomorrow")
    if delta == 2:
        return t(lang, "fmt.relative.day_after")
    if 3 <= delta <= 6:
        return _weekday_acc(lang, d.weekday())
    return f"{d.day} {_month(lang, d.month)}"


def format_date_short_with_weekday(d: date, lang: str = "ru") -> str:
    """Короткая дата с днём недели: «28 марта, суббота»."""
    weekday = _weekday_nom(lang, d.weekday())
    return f"{d.day} {_month(lang, d.month)}, {weekday}"


def format_conflict_warning(conflicts: list[Event], lang: str = "ru") -> str:
    """Предупреждение о конфликтующих по времени событиях."""
    lines = [t(lang, "fmt.conflict_warning")]
    for event in conflicts:
        time_str = event.event_time.strftime("%H:%M") if event.event_time else ""
        lines.append(f"• {event.title} ({time_str})")
    return "\n".join(lines)


def format_confirmation(
    title: str, event_date: date, event_time: time | None,
    transcript: str | None = None, conflict_warning: str | None = None,
    lang: str = "ru",
) -> str:
    """Карточка подтверждения события."""
    lines = []
    if conflict_warning:
        lines.append(conflict_warning + "\n")
    if transcript:
        lines.append(t(lang, "fmt.confirmation.transcript", transcript=transcript))
    lines.append(t(lang, "fmt.confirmation.header"))
    lines.append(f"📝 {title}")
    lines.append(f"📅 {format_date_with_weekday(event_date, lang)}")
    if event_time is not None:
        lines.append(f"⏰ {event_time.strftime('%H:%M')}")
    lines.append(t(lang, "fmt.confirmation.publish"))
    return "\n".join(lines)


def format_notification(
    space_name: str, title: str, event_date: date, event_time: time | None,
    creator_name: str, lang: str = "ru",
) -> str:
    """Уведомление участников о новом событии."""
    lines = [
        t(lang, "fmt.notification.new_event", space=space_name),
        f"📝 {title}",
        f"📅 {format_date_relative(event_date, lang).capitalize()}",
    ]
    if event_time is not None:
        lines.append(f"⏰ {event_time.strftime('%H:%M')}")
    lines.append(t(lang, "fmt.notification.added_by", name=creator_name))
    return "\n".join(lines)


def format_event_manage_card(
    title: str, event_date: date, event_time: time | None,
    lang: str = "ru",
) -> str:
    """Карточка управления событием."""
    lines = [
        t(lang, "fmt.manage.header"),
        f"📝 {title}",
        f"📅 {format_date_with_weekday(event_date, lang)}",
    ]
    if event_time is not None:
        lines.append(f"⏰ {event_time.strftime('%H:%M')}")
    return "\n".join(lines)


def format_event_edited_notification(
    space_name: str, title: str,
    changes: list[tuple[str, str, str]],
    editor_name: str, lang: str = "ru",
) -> str:
    """Уведомление участников об изменении события."""
    lines = [
        t(lang, "fmt.edited.header", space=space_name),
        f"📝 {title}",
    ]
    for field_label, old_value, new_value in changes:
        lines.append(f"🔄 {field_label}: {old_value} → {new_value}")
    lines.append(t(lang, "fmt.edited.changed_by", name=editor_name))
    return "\n".join(lines)


def format_event_deleted_notification(
    space_name: str, title: str, editor_name: str,
    event_date: date | None = None, event_time: time | None = None,
    lang: str = "ru",
) -> str:
    """Уведомление участников об удалении события."""
    lines = [
        t(lang, "fmt.deleted.header", space=space_name),
        f"📝 {title}",
    ]
    if event_date is not None:
        date_str = format_date_short_with_weekday(event_date, lang)
        if event_time is not None:
            date_str += f", {event_time.strftime('%H:%M')}"
        lines.append(f"📅 {date_str}")
    lines.append(t(lang, "fmt.deleted.deleted_by", name=editor_name))
    return "\n".join(lines)


def format_space_deleted_notification(
    space_name: str, admin_name: str, lang: str = "ru",
) -> str:
    """Уведомление участников об удалении пространства."""
    return t(lang, "fmt.space_deleted", name=space_name, admin=admin_name)
