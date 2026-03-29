from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.i18n import get_reminder_labels

REMINDER_KEYS_ORDER = ["1d", "2h", "1h", "30m", "15m", "0m"]


def reminder_settings_keyboard(user_settings: dict, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура toggle-кнопок для настроек напоминаний."""
    labels = get_reminder_labels(lang)
    buttons = []
    for key in REMINDER_KEYS_ORDER:
        enabled = user_settings.get(key, False)
        icon = "☑" if enabled else "☐"
        label = labels[key]
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {label}",
                callback_data=f"reminder_toggle:{key}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
