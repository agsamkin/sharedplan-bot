from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def event_manage_keyboard(event_id: UUID) -> InlineKeyboardMarkup:
    """Карточка управления событием: Изменить / Удалить."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Изменить",
                    callback_data=f"event_edit_field:{event_id}:choose",
                ),
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"event_delete:{event_id}",
                ),
            ]
        ]
    )


def event_delete_confirm_keyboard(event_id: UUID) -> InlineKeyboardMarkup:
    """Подтверждение удаления события."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, удалить",
                    callback_data=f"event_delete_yes:{event_id}",
                ),
                InlineKeyboardButton(
                    text="Отмена",
                    callback_data=f"event_delete_no:{event_id}",
                ),
            ]
        ]
    )


def event_edit_field_keyboard(event_id: UUID) -> InlineKeyboardMarkup:
    """Выбор поля для редактирования: Название / Дата / Время."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Название",
                    callback_data=f"event_edit_field:{event_id}:title",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📅 Дата",
                    callback_data=f"event_edit_field:{event_id}:date",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏰ Время",
                    callback_data=f"event_edit_field:{event_id}:time",
                ),
            ],
        ]
    )


def event_edit_time_keyboard(event_id: UUID) -> InlineKeyboardMarkup:
    """Клавиатура при редактировании времени с кнопкой «Убрать время»."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚫 Убрать время (весь день)",
                    callback_data=f"event_remove_time:{event_id}",
                ),
            ]
        ]
    )


def event_edit_confirm_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение редактирования."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Сохранить",
                    callback_data="event_edit_confirm",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="event_edit_cancel",
                ),
            ]
        ]
    )
