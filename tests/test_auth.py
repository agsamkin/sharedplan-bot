"""Тесты валидации Telegram initData."""

import hashlib
import hmac
import json
import time
from urllib.parse import quote, urlencode

import pytest

from mini_app.backend.auth import validate_init_data

BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"


def _make_init_data(
    user_id: int = 12345,
    bot_token: str = BOT_TOKEN,
    auth_date: int | None = None,
    extra_params: dict | None = None,
) -> str:
    """Сгенерировать валидный initData для тестов."""
    if auth_date is None:
        auth_date = int(time.time())

    user_data = json.dumps({"id": user_id, "first_name": "Test", "username": "testuser"})
    params = {
        "user": user_data,
        "auth_date": str(auth_date),
    }
    if extra_params:
        params.update(extra_params)

    # Вычисляем хеш
    data_check_parts = [f"{k}={v}" for k, v in sorted(params.items())]
    data_check_string = "\n".join(data_check_parts)
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    params["hash"] = computed_hash
    return urlencode(params)


def test_valid_init_data():
    """Валидный initData проходит проверку и возвращает user_id."""
    init_data = _make_init_data(user_id=67890)
    result = validate_init_data(init_data, BOT_TOKEN)
    assert result == 67890


def test_invalid_hash():
    """Невалидный хеш вызывает ValueError."""
    init_data = _make_init_data()
    # Подменяем хеш
    init_data = init_data.replace(init_data.split("hash=")[1][:10], "0" * 10)
    with pytest.raises(ValueError, match="Невалидная подпись"):
        validate_init_data(init_data, BOT_TOKEN)


def test_missing_hash():
    """Отсутствующий hash вызывает ValueError."""
    auth_date = str(int(time.time()))
    user_data = json.dumps({"id": 123})
    init_data = urlencode({"user": user_data, "auth_date": auth_date})
    with pytest.raises(ValueError, match="hash"):
        validate_init_data(init_data, BOT_TOKEN)


def test_expired_init_data():
    """Просроченный initData (> 1 часа) вызывает ValueError."""
    old_auth_date = int(time.time()) - 7200  # 2 часа назад
    init_data = _make_init_data(auth_date=old_auth_date)
    with pytest.raises(ValueError, match="устарел"):
        validate_init_data(init_data, BOT_TOKEN)


def test_empty_init_data():
    """Пустой initData вызывает ValueError."""
    with pytest.raises(ValueError, match="пуст"):
        validate_init_data("", BOT_TOKEN)


def test_missing_user():
    """initData без поля user вызывает ValueError."""
    auth_date = str(int(time.time()))
    params = {"auth_date": auth_date}
    data_check_parts = [f"{k}={v}" for k, v in sorted(params.items())]
    data_check_string = "\n".join(data_check_parts)
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    params["hash"] = computed_hash
    init_data = urlencode(params)
    with pytest.raises(ValueError, match="user"):
        validate_init_data(init_data, BOT_TOKEN)


def test_wrong_bot_token():
    """Валидный initData с неправильным токеном вызывает ValueError."""
    init_data = _make_init_data(bot_token=BOT_TOKEN)
    with pytest.raises(ValueError, match="подпись"):
        validate_init_data(init_data, "wrong_token")
