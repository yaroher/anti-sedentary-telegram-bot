from __future__ import annotations

from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class TaskStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class User(Model):
    user_id = fields.BigIntField(pk=True)
    username = fields.CharField(64, null=True)
    first_name = fields.CharField(128, null=True)
    day_start = fields.CharField(5, default="11:00")
    day_end = fields.CharField(5, default="18:00")
    break_every_minutes = fields.IntField(default=45)
    flavor = fields.CharField(16, default="normal")
    language = fields.CharField(8, default="en")
    is_enabled = fields.BooleanField(default=True)
    is_deleted = fields.BooleanField(default=False)
    quiet_start = fields.CharField(5, null=True)
    quiet_end = fields.CharField(5, null=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    # effectiveness additions
    personal_difficulty_offsets: fields.JSONField = fields.JSONField(default=dict)
    baseline_completed_at = fields.DatetimeField(null=True)
    daily_goal = fields.IntField(default=5)
    streak_insurance_used_at = fields.DateField(null=True)
    last_deload_at = fields.DateField(null=True)
    eye_break_enabled = fields.BooleanField(default=False)
    hydration_enabled = fields.BooleanField(default=False)
    posture_enabled = fields.BooleanField(default=False)
    eye_break_minutes = fields.IntField(default=20)
    hydration_minutes = fields.IntField(default=60)
    posture_minutes = fields.IntField(default=45)
    user_facts = fields.TextField(null=True)

    class Meta:
        table = "users"
        indexes = (("is_enabled",),)


class DailyState(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="daily_states", on_delete=fields.CASCADE
    )
    day = fields.DateField()
    completed_count = fields.IntField(default=0)
    skipped_count = fields.IntField(default=0)
    failed_count = fields.IntField(default=0)
    streak = fields.IntField(default=0)
    pressure_level = fields.IntField(default=0)
    last_task_at = fields.DatetimeField(null=True)
    next_task_at = fields.DatetimeField(null=True)
    summary = fields.TextField(default="")
    # effectiveness additions
    water_count = fields.IntField(default=0)
    eye_breaks_done = fields.IntField(default=0)
    posture_checks_done = fields.IntField(default=0)
    daily_goal_reached = fields.BooleanField(default=False)
    daily_summary_sent_at = fields.DatetimeField(null=True)
    recovery_day = fields.BooleanField(default=False)
    best_streak_today = fields.IntField(default=0)

    class Meta:
        table = "daily_state"
        unique_together = (("user", "day"),)


class Task(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="tasks", on_delete=fields.CASCADE
    )
    day = fields.DateField()
    exercise_code = fields.CharField(64)
    title = fields.CharField(128)
    instruction = fields.TextField()
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.ACTIVE, max_length=16)
    created_at = fields.DatetimeField()
    unlock_at = fields.DatetimeField()
    completed_at = fields.DatetimeField(null=True)
    skipped_at = fields.DatetimeField(null=True)
    failed_at = fields.DatetimeField(null=True)
    nudge_count = fields.IntField(default=0)
    snooze_count = fields.IntField(default=0)
    check_question = fields.TextField(null=True)
    check_answer = fields.TextField(null=True)
    suspicious = fields.BooleanField(default=False)
    # effectiveness additions
    time_to_complete_seconds = fields.IntField(null=True)
    difficulty_rating = fields.IntField(null=True)
    suspicion_reasons: fields.JSONField = fields.JSONField(default=list)

    class Meta:
        table = "tasks"
        indexes = (
            ("user_id", "day", "status"),
            ("user_id", "status"),
            ("user_id", "day"),
        )


class ChatMessage(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="messages", on_delete=fields.CASCADE
    )
    role = fields.CharEnumField(MessageRole, max_length=16)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "messages"
        indexes = (("user_id", "created_at"),)


class Achievement(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="achievements", on_delete=fields.CASCADE
    )
    code = fields.CharField(64)
    awarded_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "achievements"
        unique_together = (("user", "code"),)


class ExerciseCalibration(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="calibrations", on_delete=fields.CASCADE
    )
    exercise_code = fields.CharField(64)
    sample_count = fields.IntField(default=0)
    median_completion_seconds = fields.IntField(default=0)
    median_difficulty = fields.FloatField(default=5.0)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "exercise_calibrations"
        unique_together = (("user", "exercise_code"),)


class BusyPeriod(Model):
    """Manual /busy NN windows or scheduled mute periods."""

    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="busy_periods", on_delete=fields.CASCADE
    )
    started_at = fields.DatetimeField()
    ends_at = fields.DatetimeField()
    reason = fields.CharField(64, default="busy")

    class Meta:
        table = "busy_periods"
        indexes = (("user_id", "ends_at"),)


class Partnership(Model):
    """Bidirectional accountability link. Two rows per partnership (one per direction)."""

    id = fields.IntField(pk=True)
    user_id_a = fields.BigIntField()
    user_id_b = fields.BigIntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    active = fields.BooleanField(default=True)

    class Meta:
        table = "partnerships"
        unique_together = (("user_id_a", "user_id_b"),)
        indexes = (("user_id_a", "active"),)


class HabitTrackEvent(Model):
    """Logs eye-break / hydration / posture acknowledgements per user per day."""

    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="habit_events", on_delete=fields.CASCADE
    )
    kind = fields.CharField(16)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "habit_track_events"
        indexes = (("user_id", "kind", "created_at"),)
