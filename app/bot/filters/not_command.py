from aiogram.filters import BaseFilter
from aiogram.types import Message


class NotCommandFilter(BaseFilter):
    """Фильтр: текстовое сообщение, не являющееся командой."""

    async def __call__(self, message: Message) -> bool:
        return bool(message.text and not message.text.startswith("/"))
