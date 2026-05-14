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
