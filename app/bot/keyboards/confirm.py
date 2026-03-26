from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
