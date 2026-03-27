from aiogram.types import BotCommand

BOT_COMMANDS = [
    BotCommand(command="start", description="Начать работу с ботом"),
    BotCommand(command="help", description="Список команд"),
    BotCommand(command="newspace", description="Создать новое пространство"),
    BotCommand(command="spaces", description="Мои пространства"),
    BotCommand(command="space_info", description="Информация о пространстве"),
    BotCommand(command="events", description="Ближайшие события"),
    BotCommand(command="reminders", description="Настройки напоминаний"),
]
