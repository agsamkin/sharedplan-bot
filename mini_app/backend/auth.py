"""Валидация initData из Telegram WebApp.

Реализует HMAC-SHA256 верификацию данных, переданных из Telegram Mini App,
согласно документации: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qs, unquote


def validate_init_data(init_data: str, bot_token: str) -> int:
    """Проверить подпись initData и вернуть user_id.

    Алгоритм:
    1. Разобрать query string initData.
    2. Извлечь hash, собрать data_check_string из остальных параметров.
    3. Вычислить HMAC-SHA256 и сравнить с полученным hash.
    4. Проверить, что auth_date не старше 1 часа.
    5. Извлечь user_id из JSON-поля "user".

    Args:
        init_data: строка initData из Telegram WebApp.
        bot_token: токен Telegram-бота.

    Returns:
        user_id (int) — Telegram ID пользователя.

    Raises:
        ValueError: если данные невалидны, подпись не совпадает или истёк срок.
    """
    if not init_data:
        raise ValueError("initData пуст")

    # Разбираем query string
    parsed = parse_qs(init_data, keep_blank_values=True)

    # Извлекаем hash
    hash_list = parsed.pop("hash", None)
    if not hash_list:
        raise ValueError("Отсутствует параметр hash в initData")
    received_hash = hash_list[0]

    # Собираем data_check_string: сортированные key=value, разделённые \n
    # parse_qs возвращает списки значений — берём первое значение каждого ключа
    data_check_parts = []
    for key in sorted(parsed.keys()):
        value = parsed[key][0]
        data_check_parts.append(f"{key}={value}")
    data_check_string = "\n".join(data_check_parts)

    # Вычисляем ключ: HMAC-SHA256("WebAppData", bot_token)
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256
    ).digest()

    # Вычисляем хеш данных
    computed_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # Сравниваем хеши (constant-time)
    if not hmac.compare_digest(computed_hash, received_hash):
        raise ValueError("Невалидная подпись initData")

    # Проверяем auth_date (не старше 1 часа)
    auth_date_list = parsed.get("auth_date")
    if not auth_date_list:
        raise ValueError("Отсутствует auth_date в initData")
    try:
        auth_date = int(auth_date_list[0])
    except (ValueError, IndexError):
        raise ValueError("Невалидный auth_date в initData")

    current_time = int(time.time())
    if current_time - auth_date > 3600:
        raise ValueError("initData устарел (старше 1 часа)")

    # Извлекаем user_id из JSON-поля "user"
    user_json_list = parsed.get("user")
    if not user_json_list:
        raise ValueError("Отсутствует поле user в initData")
    try:
        user_data = json.loads(unquote(user_json_list[0]))
        user_id = int(user_data["id"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        raise ValueError(f"Невалидные данные пользователя в initData: {e}")

    return user_id
