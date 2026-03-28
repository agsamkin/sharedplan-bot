from aiogram.types import BotCommand

BOT_COMMANDS = [
    BotCommand(command="start", description="Начать работу"),
    BotCommand(command="help", description="Список команд и помощь"),
    BotCommand(command="newspace", description="Создать пространство"),
    BotCommand(command="spaces", description="Мои пространства"),
    BotCommand(command="events", description="Ближайшие события"),
    BotCommand(command="app", description="Открыть приложение"),
]
