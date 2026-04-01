"""Тесты планировщика задач — process_due_reminders и generate_recurring_occurrences."""

import sys
from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Очистка моков
for _key in list(sys.modules):
    if _key.startswith("app.services.") or _key == "app.services":
        _mod = sys.modules[_key]
        if hasattr(_mod, "_mock_name"):
            del sys.modules[_key]
for _key in list(sys.modules):
    if _key.startswith("app.db.") or _key == "app.db.models":
        _mod = sys.modules[_key]
        if hasattr(_mod, "_mock_name"):
            del sys.modules[_key]
for _key in ["app.config", "app.db.engine"]:
    if _key in sys.modules and hasattr(sys.modules[_key], "_mock_name"):
        del sys.modules[_key]

from app.scheduler.jobs import (  # noqa: E402
    process_due_reminders,
    generate_recurring_occurrences,
)


class TestProcessDueReminders:
    @pytest.mark.asyncio
    async def test_no_reminders(self):
        """Если нет наступивших напоминаний — ничего не делаем."""
        bot = AsyncMock()
        session = AsyncMock()
        session_factory = MagicMock()
        session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("app.scheduler.jobs.get_due_reminders", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []
            await process_due_reminders(bot, session_factory)

        bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_sends_reminders(self):
        """Отправляет напоминания и помечает как отправленные."""
        bot = AsyncMock()
        bot.send_message = AsyncMock()
        session = AsyncMock()
        session_factory = MagicMock()
        session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        reminder = MagicMock()
        reminder.id = "rem-1"
        reminder.user_id = 200
        reminder.reminder_type = "2h"

        with patch("app.scheduler.jobs.get_due_reminders", new_callable=AsyncMock) as mock_get, \
             patch("app.scheduler.jobs.format_reminder_message") as mock_fmt, \
             patch("app.scheduler.jobs.mark_sent", new_callable=AsyncMock) as mock_mark:
            mock_get.return_value = [
                (reminder, "Ужин", date(2026, 4, 1), time(19, 0), "Семья", "ru"),
            ]
            mock_fmt.return_value = "Напоминание: Ужин"
            await process_due_reminders(bot, session_factory)

        bot.send_message.assert_called_once_with(200, "Напоминание: Ужин")
        mock_mark.assert_called_once()
        session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_failure_marks_sent(self):
        """Ошибка отправки всё равно помечает напоминание как отправленное."""
        bot = AsyncMock()
        bot.send_message = AsyncMock(side_effect=Exception("Telegram error"))
        session = AsyncMock()
        session_factory = MagicMock()
        session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        reminder = MagicMock()
        reminder.id = "rem-1"
        reminder.user_id = 200
        reminder.reminder_type = "1h"

        with patch("app.scheduler.jobs.get_due_reminders", new_callable=AsyncMock) as mock_get, \
             patch("app.scheduler.jobs.format_reminder_message") as mock_fmt, \
             patch("app.scheduler.jobs.mark_sent", new_callable=AsyncMock) as mock_mark:
            mock_get.return_value = [
                (reminder, "Ужин", date(2026, 4, 1), time(19, 0), "Семья", "ru"),
            ]
            mock_fmt.return_value = "Напоминание: Ужин"
            await process_due_reminders(bot, session_factory)

        mock_mark.assert_called_once()  # Помечено sent=True несмотря на ошибку
        session.commit.assert_called_once()


class TestGenerateRecurringOccurrences:
    @pytest.mark.asyncio
    async def test_no_recurring_events(self):
        """Без повторяющихся событий — ранний выход."""
        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result)

        session_factory = MagicMock()
        session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        await generate_recurring_occurrences(session_factory)
        session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_processes_recurring_events(self):
        """Обрабатывает повторяющиеся события."""
        session = AsyncMock()
        event = MagicMock()
        event.id = "evt-1"
        result = MagicMock()
        result.scalars.return_value.all.return_value = [event]
        session.execute = AsyncMock(return_value=result)

        session_factory = MagicMock()
        session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.recurrence_service.advance_parent_date", new_callable=AsyncMock) as mock_adv, \
             patch("app.services.recurrence_service.generate_occurrences", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = 3
            await generate_recurring_occurrences(session_factory)

        mock_adv.assert_called_once()
        mock_gen.assert_called_once()
        session.commit.assert_called_once()
