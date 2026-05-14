from __future__ import annotations

from datetime import timedelta

from ..db.models import Task, TaskStatus, User
from ..utils.time import now, today

MAX_SNOOZE_COUNT = 2


async def get_active(user: User) -> Task | None:
    return await Task.filter(user=user, day=today(), status=TaskStatus.ACTIVE).order_by("-id").first()


async def find_for_user(task_id: int, user_id: int) -> Task | None:
    return await Task.filter(id=task_id, user_id=user_id, status=TaskStatus.ACTIVE).first()


async def find_any_for_user(task_id: int, user_id: int) -> Task | None:
    """Find a task regardless of status."""
    return await Task.filter(id=task_id, user_id=user_id).first()


async def create(
    user: User,
    exercise_code: str,
    title: str,
    instruction: str,
    unlock_at: object,
    created_at: object,
    check_question: str | None,
) -> Task:
    from ..db.models import TaskStatus

    return await Task.create(
        user=user,
        day=today(),
        exercise_code=exercise_code,
        title=title,
        instruction=instruction,
        status=TaskStatus.ACTIVE,
        created_at=created_at,
        unlock_at=unlock_at,
        check_question=check_question,
    )


async def mark_completed(task: Task) -> None:
    task.status = TaskStatus.COMPLETED
    task.completed_at = now()
    await task.save(update_fields=["status", "completed_at"])


async def mark_skipped(task: Task) -> None:
    task.status = TaskStatus.SKIPPED
    task.skipped_at = now()
    await task.save(update_fields=["status", "skipped_at"])


async def mark_failed(task: Task) -> None:
    task.status = TaskStatus.FAILED
    task.failed_at = now()
    await task.save(update_fields=["status", "failed_at"])


async def bump_nudge(task: Task) -> None:
    task.nudge_count += 1
    await task.save(update_fields=["nudge_count"])


async def skip_check_question(task_id: int, user_id: int) -> None:
    await Task.filter(id=task_id, user_id=user_id).update(check_answer="[question skipped]")


async def snooze(task: Task, minutes: int) -> Task | None:
    """Bump snooze_count and push unlock_at forward by *minutes*.

    Returns None (refused) when snooze_count has already reached MAX_SNOOZE_COUNT.
    The task must be ACTIVE; caller is responsible for that check.
    """
    if task.snooze_count >= MAX_SNOOZE_COUNT:
        return None
    task.snooze_count += 1
    task.unlock_at = task.unlock_at + timedelta(minutes=minutes)
    await task.save(update_fields=["snooze_count", "unlock_at"])
    return task
