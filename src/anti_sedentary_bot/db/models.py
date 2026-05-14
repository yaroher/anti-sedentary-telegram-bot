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

    # Adaptive difficulty: JSON dict mapping exercise_code -> int offset (-5..+10)
    personal_difficulty_offsets: fields.Field = fields.JSONField(default=dict)

    # Daily goal (number of tasks per day)
    daily_goal = fields.IntField(default=5)

    # Baseline calibration
    baseline_completed_at = fields.DatetimeField(null=True)

    # Progressive overload / deload tracking
    last_deload_at = fields.DateField(null=True)

    # Streak insurance: track when last used (ISO week string "YYYY-Www")
    streak_insurance_used_week = fields.CharField(16, null=True)

    # Health tracks (eye/hydration/posture)
    eye_break_enabled = fields.BooleanField(default=False)
    hydration_enabled = fields.BooleanField(default=False)
    posture_enabled = fields.BooleanField(default=False)
    eye_break_minutes = fields.IntField(default=20)
    hydration_minutes = fields.IntField(default=60)
    posture_minutes = fields.IntField(default=45)

    # LLM-curated stable facts about the user (injuries, preferences)
    user_facts = fields.TextField(null=True)

    # Re-engagement cooldown — set when a re-engage message was sent
    reengaged_at = fields.DatetimeField(null=True)

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

    # Daily goal tracking
    daily_goal_reached = fields.BooleanField(default=False)

    # Recovery day flag (Wednesday by default, per ISO week)
    recovery_day = fields.BooleanField(default=False)

    # Best streak today
    best_streak = fields.IntField(default=0)

    # Health track counters
    water_count = fields.IntField(default=0)
    eye_breaks_done = fields.IntField(default=0)
    posture_checks_done = fields.IntField(default=0)

    # Daily summary marker
    daily_summary_sent_at = fields.DatetimeField(null=True)

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

    # Anti-cheat and calibration
    suspicion_reasons: fields.Field = fields.JSONField(default=list)
    difficulty_rating = fields.IntField(null=True)  # 1-10 self-reported
    time_to_complete_seconds = fields.FloatField(null=True)

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
    earned_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "achievements"
        indexes = (("user_id", "code"),)


class ExerciseCalibration(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="calibrations", on_delete=fields.CASCADE
    )
    exercise_code = fields.CharField(64)
    sample_count = fields.IntField(default=0)
    median_completion_seconds = fields.FloatField(default=0.0)
    last_difficulty_rating = fields.IntField(null=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "exercise_calibrations"
        unique_together = (("user", "exercise_code"),)


class BusyPeriod(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="busy_periods", on_delete=fields.CASCADE
    )
    reason = fields.CharField(32)  # "did" or "busy"
    ends_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "busy_periods"
        indexes = (("user_id", "ends_at"),)


class Partnership(Model):
    """Bidirectional accountability link. Two rows per partnership (one per direction).

    `accepted` becomes True only after the other user clicks Accept.
    `active` is a kill-switch for /unpartner.
    """

    id = fields.IntField(pk=True)
    user_id_a = fields.BigIntField()
    user_id_b = fields.BigIntField()
    active = fields.BooleanField(default=True)
    accepted = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "partnerships"
        unique_together = (("user_id_a", "user_id_b"),)
        indexes = (("user_id_a", "active", "accepted"),)


class HabitTrackEvent(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="habit_events", on_delete=fields.CASCADE
    )
    event_type = fields.CharField(64)
    payload: fields.Field = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "habit_track_events"
        indexes = (("user_id", "created_at"),)
