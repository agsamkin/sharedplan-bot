from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.i18n import t


def event_confirm_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Inline-кнопки подтверждения события: Да / Изменить / Отмена."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "kb.confirm.yes"),
                    callback_data="event_confirm",
                ),
                InlineKeyboardButton(
                    text=t(lang, "kb.confirm.edit"),
                    callback_data="event_edit",
                ),
                InlineKeyboardButton(
                    text=t(lang, "kb.confirm.cancel"),
                    callback_data="event_cancel",
                ),
            ]
        ]
    )


def event_past_date_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Inline-кнопки для подтверждения события с прошедшей датой."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "kb.confirm.past_confirm"),
                    callback_data="event_past_confirm",
                ),
                InlineKeyboardButton(
                    text=t(lang, "kb.confirm.past_cancel"),
                    callback_data="event_past_cancel",
                ),
            ]
        ]
    )


def delete_space_confirm_keyboard(space_id: UUID, lang: str = "ru") -> InlineKeyboardMarkup:
    """Inline-кнопки подтверждения удаления пространства."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "kb.confirm.delete_yes"),
                    callback_data=f"delete_space_confirm:{space_id}",
                ),
                InlineKeyboardButton(
                    text=t(lang, "kb.confirm.delete_cancel"),
                    callback_data=f"delete_space_cancel:{space_id}",
                ),
            ]
        ]
    )
