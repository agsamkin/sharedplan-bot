"""Тесты для динамической генерации промпта парсера событий."""

from datetime import date, time

import pytest

from app.prompts.event_parser import (
    build_examples,
    build_system_prompt,
    build_messages,
    build_messages_reinforced,
    next_weekday,
    REINFORCED_SUFFIX,
)


class TestNextWeekday:
    """Тесты next_weekday(current_date, target_weekday)."""

    def test_monday_from_friday(self):
        # Пятница → ближайший понедельник = +3
        assert next_weekday(date(2026, 3, 27), 0) == date(2026, 3, 30)

    def test_monday_from_monday(self):
        # Понедельник → следующий понедельник = +7
        assert next_weekday(date(2026, 3, 30), 0) == date(2026, 4, 6)

    def test_wednesday_from_monday(self):
        # Понедельник → среда = +2
        assert next_weekday(date(2026, 3, 30), 2) == date(2026, 4, 1)

    def test_friday_from_saturday(self):
        # Суббота → пятница = +6
        assert next_weekday(date(2026, 3, 28), 4) == date(2026, 4, 3)

    def test_sunday_from_saturday(self):
        # Суббота → воскресенье = +1
        assert next_weekday(date(2026, 3, 28), 6) == date(2026, 3, 29)

    def test_sunday_from_sunday(self):
        # Воскресенье → следующее воскресенье = +7
        assert next_weekday(date(2026, 3, 29), 6) == date(2026, 4, 5)

    @pytest.mark.parametrize("target_weekday", range(7))
    def test_always_in_future(self, target_weekday):
        """Результат всегда строго в будущем (не сегодня)."""
        today = date(2026, 3, 29)
        result = next_weekday(today, target_weekday)
        assert result > today

    @pytest.mark.parametrize("target_weekday", range(7))
    def test_correct_weekday(self, target_weekday):
        """Результат — правильный день недели."""
        today = date(2026, 3, 29)
        result = next_weekday(today, target_weekday)
        assert result.weekday() == target_weekday

    def test_month_boundary(self):
        # 31 марта (вторник) → среда = 1 апреля
        assert next_weekday(date(2026, 3, 31), 2) == date(2026, 4, 1)

    def test_year_boundary(self):
        # 31 декабря (среда) → четверг = 1 января
        assert next_weekday(date(2025, 12, 31), 3) == date(2026, 1, 1)


class TestBuildExamples:
    """Тесты build_examples — даты в примерах консистентны с current_date."""

    def test_contains_tomorrow_date(self):
        today = date(2026, 3, 29)
        examples = build_examples(today)
        tomorrow = "2026-03-30"
        # Пример «завтра в 19:00» должен содержать дату завтра
        assert f'"date": "{tomorrow}"' in examples

    def test_no_hardcoded_dates(self):
        """Примеры не содержат хардкоженных дат из старого промпта."""
        today = date(2026, 3, 29)
        examples = build_examples(today)
        # Старые хардкоженные даты из оригинального промпта
        assert "2026-03-27" not in examples
        assert "2026-03-28" not in examples

    def test_monday_example_correct(self):
        # Воскресенье 29 марта → понедельник = 30 марта
        today = date(2026, 3, 29)
        examples = build_examples(today)
        assert '"date": "2026-03-30"' in examples  # понедельник

    def test_day_after_tomorrow_correct(self):
        today = date(2026, 3, 29)
        examples = build_examples(today)
        assert '"date": "2026-03-31"' in examples  # послезавтра

    def test_today_example_present(self):
        """Пример «сегодня вечером» содержит текущую дату."""
        today = date(2026, 3, 29)
        examples = build_examples(today)
        assert "Сегодня вечером ужин" in examples
        assert f'"date": "{today}"' in examples

    def test_relative_time_example_with_current_time(self):
        """Пример «через 2 часа» генерируется при наличии current_time."""
        today = date(2026, 3, 29)
        ct = time(14, 0)
        examples = build_examples(today, ct)
        assert "Через 2 часа встреча" in examples
        assert '"time": "16:00"' in examples

    def test_relative_time_example_without_current_time(self):
        """Без current_time пример «через 2 часа» не генерируется."""
        today = date(2026, 3, 29)
        examples = build_examples(today)
        assert "Через 2 часа встреча" not in examples

    def test_relative_time_midnight_crossover(self):
        """Через 2 часа при 23:00 → переход на следующий день."""
        today = date(2026, 3, 29)
        ct = time(23, 0)
        examples = build_examples(today, ct)
        assert '"date": "2026-03-30"' in examples
        assert '"time": "01:00"' in examples

    def test_header_contains_current_date(self):
        today = date(2026, 3, 29)
        examples = build_examples(today)
        assert "при дате 2026-03-29, воскресенье" in examples

    def test_different_dates_produce_different_examples(self):
        """Разные даты дают разные примеры."""
        ex1 = build_examples(date(2026, 3, 29))
        ex2 = build_examples(date(2026, 4, 15))
        assert ex1 != ex2


class TestBuildSystemPrompt:
    """Тесты build_system_prompt — структура и содержание промпта."""

    def test_contains_priority_instruction(self):
        prompt = build_system_prompt(date(2026, 3, 29), time(14, 0))
        assert "КРИТИЧЕСКИ ВАЖНО" in prompt
        assert "вычисляй ТОЛЬКО от указанной выше даты" in prompt

    def test_contains_tomorrow_anchor(self):
        prompt = build_system_prompt(date(2026, 3, 29))
        assert "«завтра» = 2026-03-30" in prompt

    def test_contains_current_date(self):
        prompt = build_system_prompt(date(2026, 3, 29))
        assert "Сегодня: 2026-03-29 (воскресенье)" in prompt

    def test_contains_current_time(self):
        prompt = build_system_prompt(date(2026, 3, 29), time(14, 30))
        assert "текущее время: 14:30" in prompt

    def test_contains_examples(self):
        prompt = build_system_prompt(date(2026, 3, 29))
        assert "Примеры (при дате 2026-03-29" in prompt
        assert "Ужин с родителями завтра" in prompt

    def test_footer_at_end(self):
        prompt = build_system_prompt(date(2026, 3, 29))
        assert prompt.strip().endswith("Отвечай ТОЛЬКО JSON.")

    def test_no_old_hardcoded_dates(self):
        prompt = build_system_prompt(date(2026, 4, 10))
        assert "2026-03-27" not in prompt
        assert "2026-03-28" not in prompt


class TestBuildMessages:
    """Тесты build_messages и build_messages_reinforced."""

    def test_build_messages_structure(self):
        msgs = build_messages("Встреча завтра", date(2026, 3, 29), time(14, 30))
        assert len(msgs) == 2
        assert msgs[0]["role"] == "system"
        assert msgs[1]["role"] == "user"
        assert msgs[1]["content"] == "<user_input>Встреча завтра</user_input>"

    def test_build_messages_system_content(self):
        msgs = build_messages("Тест", date(2026, 3, 29), time(14, 0))
        system = msgs[0]["content"]
        assert "Сегодня: 2026-03-29" in system
        assert "«завтра» = 2026-03-30" in system

    def test_build_messages_reinforced_has_suffix(self):
        msgs = build_messages_reinforced("Тест", date(2026, 3, 29))
        system = msgs[0]["content"]
        assert REINFORCED_SUFFIX.strip() in system

    def test_weekday_param_ignored(self):
        """Параметр weekday сохранён для совместимости, но не влияет на результат."""
        msgs1 = build_messages("Тест", date(2026, 3, 29), weekday="пятница")
        msgs2 = build_messages("Тест", date(2026, 3, 29), weekday=None)
        assert msgs1[0]["content"] == msgs2[0]["content"]


class TestPromptScenarioCoverage:
    """Тесты покрытия LLM-сценариев: промпт содержит корректные данные для модели."""

    def test_tomorrow_scenario(self):
        """Scenario: 'завтра' при 2026-03-29 → пример указывает на 2026-03-30."""
        prompt = build_system_prompt(date(2026, 3, 29), time(14, 0))
        assert "Сегодня: 2026-03-29" in prompt
        assert "«завтра» = 2026-03-30" in prompt
        assert '"date": "2026-03-30", "time": "19:00"' in prompt

    def test_today_evening_scenario(self):
        """Scenario: 'сегодня вечером' → пример с текущей датой и 19:00."""
        prompt = build_system_prompt(date(2026, 3, 29))
        assert "Сегодня вечером ужин" in prompt
        assert '"date": "2026-03-29", "time": "19:00"' in prompt

    def test_day_after_tomorrow_scenario(self):
        """Scenario: 'послезавтра после обеда' → дата +2, время 14:00."""
        prompt = build_system_prompt(date(2026, 3, 29))
        assert "Стоматолог послезавтра после обеда" in prompt
        assert '"date": "2026-03-31", "time": "14:00"' in prompt

    def test_next_week_wednesday_scenario(self):
        """Scenario: 'на следующей неделе в среду вечером' от вс 29.03 → 01.04."""
        prompt = build_system_prompt(date(2026, 3, 29))
        assert "на следующей неделе в среду вечером" in prompt
        assert '"date": "2026-04-01", "time": "19:00"' in prompt

    def test_implicit_title_scenario(self):
        """Scenario: 'Сходить к врачу' → title='Визит к врачу', time=09:00."""
        prompt = build_system_prompt(date(2026, 3, 29))
        assert "Сходить к врачу завтра утром" in prompt
        assert '"title": "Визит к врачу"' in prompt
        assert '"time": "09:00"' in prompt

    def test_month_boundary(self):
        """31 марта → 'завтра' = 1 апреля (граница месяца)."""
        prompt = build_system_prompt(date(2026, 3, 31))
        assert '"date": "2026-04-01"' in prompt
        assert "«завтра» = 2026-04-01" in prompt

    def test_year_boundary(self):
        """31 декабря → 'завтра' = 1 января следующего года."""
        prompt = build_system_prompt(date(2026, 12, 31))
        assert '"date": "2027-01-01"' in prompt
        assert "«завтра» = 2027-01-01" in prompt
