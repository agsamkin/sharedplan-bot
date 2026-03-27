from datetime import date

WEEKDAYS_RU = [
    "понедельник", "вторник", "среда", "четверг",
    "пятница", "суббота", "воскресенье",
]

SYSTEM_PROMPT = """\
Ты — парсер событий. Извлеки из текста пользователя название события, дату и время.

Сегодня: {current_date} ({weekday}), часовой пояс: Europe/Moscow.

Верни ТОЛЬКО валидный JSON в формате:
{{"title": "название события", "date": "YYYY-MM-DD", "time": "HH:MM"}}

Правила:
- "date" — всегда в формате YYYY-MM-DD
- "time" — в формате HH:MM или null, если время не указано
- Разрешай относительные даты: «завтра» = следующий день, «в понедельник» = ближайший понедельник (если сегодня понедельник — следующий), «через N дней» = текущая дата + N
- Разрешай разговорные выражения времени: «утром» = 09:00, «днём» = 14:00, «вечером» = 19:00, «после обеда» = 14:00, «в 8 утра» = 08:00, «в 9 вечера» = 21:00
- Если время не указано явно или косвенно — "time": null
- Название должно быть кратким и осмысленным
- Не добавляй информацию, которой нет в тексте
- Отвечай ТОЛЬКО JSON, без пояснений\
"""

REINFORCED_SUFFIX = "\n\nВАЖНО: Ответь ТОЛЬКО валидным JSON. Никакого текста до или после JSON."


def build_messages(
    user_text: str,
    current_date: date,
    weekday: str | None = None,
) -> list[dict[str, str]]:
    if weekday is None:
        weekday = WEEKDAYS_RU[current_date.weekday()]

    system_content = SYSTEM_PROMPT.format(
        current_date=current_date.isoformat(),
        weekday=weekday,
    )

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_text},
    ]


def build_messages_reinforced(
    user_text: str,
    current_date: date,
    weekday: str | None = None,
) -> list[dict[str, str]]:
    if weekday is None:
        weekday = WEEKDAYS_RU[current_date.weekday()]

    system_content = SYSTEM_PROMPT.format(
        current_date=current_date.isoformat(),
        weekday=weekday,
    ) + REINFORCED_SUFFIX

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_text},
    ]
