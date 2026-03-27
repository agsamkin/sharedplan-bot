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
- Разрешай относительные даты: «завтра» = следующий день, «в понедельник» = ближайший понедельник (если сегодня понедельник — следующий), «через N дней» = текущая дата + N, «на следующей неделе в среду» = среда следующей недели
- Разрешай относительное время: «через N минут» = текущее время + N минут, «через N часов» = текущее время + N часов, «через полчаса» = текущее время + 30 минут. Если результат переходит за полночь — увеличь дату на 1 день
- Разговорные выражения времени: «утром» = 09:00, «днём» = 14:00, «вечером» = 19:00, «ночью» = 22:00, «после обеда» = 14:00, «в обед» = 13:00, «в 8 утра» = 08:00, «в 9 вечера» = 21:00
- Если время не указано явно или косвенно — "time": null
- Название должно сохранять все важные детали из текста: имена, места, номера кабинетов, адреса и прочие уточнения. Из названия убирай только дату и время начала
- Если указан временной интервал (например, «08:00 - 09:30»), в "time" поставь время начала, а интервал сохрани в названии (например, «08:00–09:30 Событие»)
- Не добавляй информацию, которой нет в тексте
- Отвечай ТОЛЬКО JSON, без пояснений

Примеры (при дате 2026-03-27, пятница):

Текст: «Ужин с родителями завтра в 19:00»
{{"title": "Ужин с родителями", "date": "2026-03-28", "time": "19:00"}}

Текст: «Тренировка в понедельник в 8 утра»
{{"title": "Тренировка", "date": "2026-03-30", "time": "08:00"}}

Текст: «День рождения Ани 5 апреля»
{{"title": "День рождения Ани", "date": "2026-04-05", "time": null}}

Текст: «Стоматолог послезавтра после обеда, ул. Ленина 5»
{{"title": "Стоматолог, ул. Ленина 5", "date": "2026-03-29", "time": "14:00"}}

Текст: «01.04 13:10 Хирург 15 каб»
{{"title": "Хирург, 15 каб.", "date": "2026-04-01", "time": "13:10"}}

Текст: «15.04 08:00 - 09:30 Анализ мочи и крови»
{{"title": "08:00–09:30 Анализ мочи и крови", "date": "2026-04-15", "time": "08:00"}}

Текст: «Созвон с Петей на следующей неделе в среду вечером»
{{"title": "Созвон с Петей", "date": "2026-04-01", "time": "19:00"}}

Текст: «Сходить к врачу завтра утром»
{{"title": "Визит к врачу", "date": "2026-03-28", "time": "09:00"}}

Текст: «Новый год»
{{"title": "Новый год", "date": "2027-01-01", "time": null}}\
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
