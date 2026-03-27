from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def event_confirm_keyboard() -> InlineKeyboardMarkup:
    """Inline-кнопки подтверждения события: Да / Изменить / Отмена."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data="event_confirm",
                ),
                InlineKeyboardButton(
                    text="✏️ Изменить",
                    callback_data="event_edit",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="event_cancel",
                ),
            ]
        ]
    )


def event_past_date_keyboard() -> InlineKeyboardMarkup:
    """Inline-кнопки для подтверждения события с прошедшей датой."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Всё равно создать",
                    callback_data="event_past_confirm",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="event_past_cancel",
                ),
            ]
        ]
    )


def delete_space_confirm_keyboard(space_id: UUID) -> InlineKeyboardMarkup:
    """Inline-кнопки подтверждения удаления пространства."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, удалить",
                    callback_data=f"delete_space_confirm:{space_id}",
                ),
                InlineKeyboardButton(
                    text="Отмена",
                    callback_data=f"delete_space_cancel:{space_id}",
                ),
            ]
        ]
    )
