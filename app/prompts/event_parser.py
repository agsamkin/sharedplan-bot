from datetime import date, time, timedelta

WEEKDAYS_RU = [
    "понедельник", "вторник", "среда", "четверг",
    "пятница", "суббота", "воскресенье",
]

PROMPT_HEADER = """\
Ты — парсер событий. Извлеки из текста пользователя название события, дату и время.

Сегодня: {current_date} ({weekday}), текущее время: {current_time}, часовой пояс: Europe/Moscow.

КРИТИЧЕСКИ ВАЖНО: Все относительные даты (завтра, в понедельник, через 3 дня) вычисляй ТОЛЬКО от указанной выше даты «Сегодня». Примеры ниже приведены для этой же даты.

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
- ВАЖНО: Если после предлога «в» стоит конструкция «ЧЧ-ММ» (где ММ < 60), это время с минутами, а НЕ диапазон. Например: «в 14-15» = 14:15, «в 9-30» = 09:30, «в 10-45» = 10:45
- Временной интервал (диапазон) определяется ТОЛЬКО при формате «HH:MM - HH:MM» (с двоеточием) или конструкции «с X до Y» / «от X до Y». В этом случае в "time" поставь время начала, а интервал сохрани в названии (например, «08:00–09:30 Событие»)
- Не добавляй информацию, которой нет в тексте
- Отвечай ТОЛЬКО JSON, без пояснений\
"""

PROMPT_FOOTER = """
Помни: «завтра» = {tomorrow_date}, текущая дата для всех вычислений — {current_date}. Отвечай ТОЛЬКО JSON."""

REINFORCED_SUFFIX = "\n\nВАЖНО: Ответь ТОЛЬКО валидным JSON. Никакого текста до или после JSON."


def next_weekday(current_date: date, target_weekday: int) -> date:
    """Ближайший будущий день недели (0=пн, 6=вс).

    Если сегодня = target, возвращает через 7 дней.
    """
    days_ahead = target_weekday - current_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return current_date + timedelta(days=days_ahead)


def _next_week_weekday(current_date: date, target_weekday: int) -> date:
    """День недели на СЛЕДУЮЩЕЙ неделе."""
    days_to_next_monday = 7 - current_date.weekday()
    next_monday = current_date + timedelta(days=days_to_next_monday)
    return next_monday + timedelta(days=target_weekday)


def _future_month_day(current_date: date, month: int, day: int) -> date:
    """Ближайшая будущая дата с указанным месяцем и днём."""
    target = current_date.replace(month=month, day=day)
    if target <= current_date:
        target = target.replace(year=target.year + 1)
    return target


def _add_hours(base_time: time, hours: int) -> tuple[time, int]:
    """Добавляет часы к времени. Возвращает (new_time, extra_days)."""
    total_minutes = base_time.hour * 60 + base_time.minute + hours * 60
    extra_days = total_minutes // (24 * 60)
    remaining = total_minutes % (24 * 60)
    return time(remaining // 60, remaining % 60), extra_days


def build_examples(current_date: date, current_time: time | None = None) -> str:
    """Генерирует few-shot примеры с датами, вычисленными от current_date."""
    weekday = WEEKDAYS_RU[current_date.weekday()]
    tomorrow = current_date + timedelta(days=1)
    day_after_tomorrow = current_date + timedelta(days=2)
    next_monday = next_weekday(current_date, 0)
    next_week_wed = _next_week_weekday(current_date, 2)
    apr5 = _future_month_day(current_date, 4, 5)
    new_year = date(current_date.year + 1, 1, 1)
    abs_date_near = current_date + timedelta(days=10)
    abs_date_far = current_date + timedelta(days=20)

    # Декларативный список: (текст_ввода, заголовок, дата, время)
    examples: list[tuple[str, str, date, str | None]] = [
        ("Ужин с родителями завтра в 19:00", "Ужин с родителями", tomorrow, "19:00"),
        ("Тренировка в понедельник в 8 утра", "Тренировка", next_monday, "08:00"),
        ("День рождения Ани 5 апреля", "День рождения Ани", apr5, None),
        ("Стоматолог послезавтра после обеда, ул. Ленина 5", "Стоматолог, ул. Ленина 5", day_after_tomorrow, "14:00"),
        (f'{abs_date_near.strftime("%d.%m")} 13:10 Хирург 15 каб', "Хирург, 15 каб.", abs_date_near, "13:10"),
        (f'{abs_date_far.strftime("%d.%m")} 08:00 - 09:30 Анализ мочи и крови', "08:00–09:30 Анализ мочи и крови", abs_date_far, "08:00"),
        ("Созвон с Петей на следующей неделе в среду вечером", "Созвон с Петей", next_week_wed, "19:00"),
        ("Завтра обед в 14-15 с Леной", "Обед с Леной", tomorrow, "14:15"),
        ("Встреча с 14 до 15 завтра", "14:00–15:00 Встреча", tomorrow, "14:00"),
        ("Сходить к врачу завтра утром", "Визит к врачу", tomorrow, "09:00"),
        ("Новый год", "Новый год", new_year, None),
        ("Сегодня вечером ужин", "Ужин", current_date, "19:00"),
    ]

    if current_time:
        new_time, extra_days = _add_hours(current_time, 2)
        target_date = current_date + timedelta(days=extra_days)
        examples.append(("Через 2 часа встреча", "Встреча", target_date, new_time.strftime("%H:%M")))

    lines = [f"Примеры (при дате {current_date}, {weekday}):"]
    for input_text, title, ex_date, ex_time in examples:
        time_json = f'"{ex_time}"' if ex_time else "null"
        lines.append(
            f'Текст: «{input_text}»\n'
            f'{{"title": "{title}", "date": "{ex_date}", "time": {time_json}}}'
        )

    return "\n\n".join(lines)


def build_system_prompt(current_date: date, current_time: time | None = None) -> str:
    """Собирает полный системный промпт с динамическими примерами."""
    weekday = WEEKDAYS_RU[current_date.weekday()]
    tomorrow = current_date + timedelta(days=1)

    header = PROMPT_HEADER.format(
        current_date=current_date.isoformat(),
        current_time=current_time.strftime("%H:%M") if current_time else "unknown",
        weekday=weekday,
    )

    examples = build_examples(current_date, current_time)

    footer = PROMPT_FOOTER.format(
        tomorrow_date=tomorrow.isoformat(),
        current_date=current_date.isoformat(),
    )

    return header + "\n\n" + examples + footer


def build_messages(
    user_text: str,
    current_date: date,
    current_time: time | None = None,
    weekday: str | None = None,
) -> list[dict[str, str]]:
    system_content = build_system_prompt(current_date, current_time)
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
    system_content = build_system_prompt(current_date, current_time) + REINFORCED_SUFFIX
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_text},
    ]
