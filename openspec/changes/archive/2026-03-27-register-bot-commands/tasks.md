## 1. Определение списка команд

- [x] 1.1 Создать модуль `app/bot/commands.py` с константой `BOT_COMMANDS` — список `BotCommand` с 7 командами и описаниями на русском

## 2. Регистрация команд при старте

- [x] 2.1 В `app/main.py` импортировать `BOT_COMMANDS` и вызвать `bot.set_my_commands(BOT_COMMANDS)` после `bot.get_me()` и до `dp.start_polling()`

## 3. Проверка

- [x] 3.1 Запустить бота и убедиться, что команды отображаются в меню Telegram
