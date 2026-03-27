from datetime import date, time

WEEKDAYS_RU = [
    "понедельник", "вторник", "среда", "четверг",
    "пятница", "суббота", "воскресенье",
]

SYSTEM_PROMPT = """\
Ты — парсер событий. Извлеки из текста пользователя название события, дату и время.

Сегодня: {current_date} ({weekday}), текущее время: {current_time}, часовой пояс: Europe/Moscow.

Верни ТОЛЬКО валидный JSON в формате:
{{"title": "название события", "date": "YYYY-MM-DD", "time": "HH:MM"}}

Правила:
- "date" — всегда в формате YYYY-MM-DD
- "time" — в формате HH:MM или null, если время не указано
- Разрешай относительные даты: «завтра» = следующий день, «в понедельник» = ближайший понедельник (если сегодня понедельник — следующий), «через N дней» = текущая дата + N
- Разрешай относительное время: «через N минут» = текущее время + N минут, «через N часов» = текущее время + N часов, «через полчаса» = текущее время + 30 минут. Если результат переходит за полночь — увеличь дату на 1 день
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
    current_time: time | None = None,
    weekday: str | None = None,
) -> list[dict[str, str]]:
    if weekday is None:
        weekday = WEEKDAYS_RU[current_date.weekday()]

    system_content = SYSTEM_PROMPT.format(
        current_date=current_date.isoformat(),
        current_time=current_time.strftime("%H:%M") if current_time else "unknown",
        weekday=weekday,
    )

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_text},
    ]


def build_messages_reinforced(
    user_text: str,
    current_date: date,
    current_time: time | None = None,
    weekday: str | None = None,
) -> list[dict[str, str]]:
    if weekday is None:
        weekday = WEEKDAYS_RU[current_date.weekday()]

    system_content = SYSTEM_PROMPT.format(
        current_date=current_date.isoformat(),
        current_time=current_time.strftime("%H:%M") if current_time else "unknown",
        weekday=weekday,
    ) + REINFORCED_SUFFIX

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_text},
    ]
