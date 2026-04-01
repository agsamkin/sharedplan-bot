"""Тесты конфигурации приложения."""

from unittest.mock import patch
import os

import pytest


class TestSettings:
    def test_settings_loads(self):
        """Settings загружается и содержит обязательные поля."""
        from app.config import settings
        assert hasattr(settings, "TELEGRAM_BOT_TOKEN")
        assert hasattr(settings, "DATABASE_URL")
        assert hasattr(settings, "TIMEZONE")
        assert hasattr(settings, "REMINDER_CHECK_INTERVAL_SECONDS")
        assert hasattr(settings, "MINI_APP_URL")
        assert hasattr(settings, "MINI_APP_PORT")
        assert hasattr(settings, "OWNER_TELEGRAM_ID")

    def test_timezone_default(self):
        from app.config import Settings
        # Defaults check at class level
        assert Settings.model_fields["TIMEZONE"].default == "Europe/Moscow"

    def test_reminder_interval_default(self):
        from app.config import Settings
        assert Settings.model_fields["REMINDER_CHECK_INTERVAL_SECONDS"].default == 30

    def test_mini_app_port_default(self):
        from app.config import Settings
        assert Settings.model_fields["MINI_APP_PORT"].default == 8080

    def test_optional_api_keys(self):
        from app.config import Settings
        assert Settings.model_fields["OPENROUTER_API_KEY"].default is None
        assert Settings.model_fields["NEXARA_API_KEY"].default is None
