from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def space_select_keyboard(
    spaces: list[dict], action: str
) -> InlineKeyboardMarkup:
    """Inline-клавиатура выбора пространства.

    callback_data: space_select:{space_id}:{action}
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=s["name"],
                callback_data=f"space_select:{s['id']}:{action}",
            )
        ]
        for s in spaces
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
