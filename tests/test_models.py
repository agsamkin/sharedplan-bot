"""Тесты моделей БД — проверка определений и дефолтов."""

import uuid
from datetime import date, datetime, time

from app.db.models import (
    Base,
    User,
    Space,
    UserSpace,
    Event,
    ScheduledReminder,
    DEFAULT_REMINDER_SETTINGS,
)


class TestDefaultReminderSettings:
    def test_has_all_keys(self):
        assert set(DEFAULT_REMINDER_SETTINGS.keys()) == {"1d", "2h", "1h", "30m", "15m", "0m"}

    def test_default_enabled(self):
        assert DEFAULT_REMINDER_SETTINGS["1d"] is True
        assert DEFAULT_REMINDER_SETTINGS["2h"] is True
        assert DEFAULT_REMINDER_SETTINGS["15m"] is True
        assert DEFAULT_REMINDER_SETTINGS["0m"] is True

    def test_default_disabled(self):
        assert DEFAULT_REMINDER_SETTINGS["1h"] is False
        assert DEFAULT_REMINDER_SETTINGS["30m"] is False


class TestUserModel:
    def test_tablename(self):
        assert User.__tablename__ == "users"

    def test_columns_exist(self):
        cols = {c.name for c in User.__table__.columns}
        assert "id" in cols
        assert "username" in cols
        assert "first_name" in cols
        assert "reminder_settings" in cols
        assert "language" in cols
        assert "created_at" in cols

    def test_language_default(self):
        col = User.__table__.columns["language"]
        assert col.default.arg == "en"


class TestSpaceModel:
    def test_tablename(self):
        assert Space.__tablename__ == "spaces"

    def test_columns_exist(self):
        cols = {c.name for c in Space.__table__.columns}
        assert "id" in cols
        assert "name" in cols
        assert "invite_code" in cols
        assert "created_by" in cols
        assert "created_at" in cols

    def test_invite_code_unique(self):
        col = Space.__table__.columns["invite_code"]
        assert col.unique is True


class TestUserSpaceModel:
    def test_tablename(self):
        assert UserSpace.__tablename__ == "user_spaces"

    def test_composite_pk(self):
        pk_cols = {c.name for c in UserSpace.__table__.primary_key.columns}
        assert pk_cols == {"user_id", "space_id"}

    def test_has_check_constraint(self):
        constraints = [c.name for c in UserSpace.__table__.constraints if hasattr(c, "name") and c.name]
        assert "ck_user_spaces_role" in constraints


class TestEventModel:
    def test_tablename(self):
        assert Event.__tablename__ == "events"

    def test_columns_exist(self):
        cols = {c.name for c in Event.__table__.columns}
        assert "id" in cols
        assert "space_id" in cols
        assert "title" in cols
        assert "event_date" in cols
        assert "event_time" in cols
        assert "created_by" in cols
        assert "raw_input" in cols
        assert "recurrence_rule" in cols
        assert "parent_event_id" in cols
        assert "created_at" in cols

    def test_has_indexes(self):
        index_names = {idx.name for idx in Event.__table__.indexes}
        assert "idx_events_space_date" in index_names
        assert "idx_events_parent" in index_names


class TestScheduledReminderModel:
    def test_tablename(self):
        assert ScheduledReminder.__tablename__ == "scheduled_reminders"

    def test_columns_exist(self):
        cols = {c.name for c in ScheduledReminder.__table__.columns}
        assert "id" in cols
        assert "event_id" in cols
        assert "user_id" in cols
        assert "remind_at" in cols
        assert "reminder_type" in cols
        assert "sent" in cols

    def test_has_index(self):
        index_names = {idx.name for idx in ScheduledReminder.__table__.indexes}
        assert "idx_reminders_remind_at_sent" in index_names


class TestBase:
    def test_declarative_base(self):
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "__subclasses__")
