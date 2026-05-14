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


# ---------------------------------------------------------------------------
# Effectiveness additions
# ---------------------------------------------------------------------------


async def record_completion_metrics(task: Task, time_to_complete_seconds: int) -> None:
    """Persist the wall-clock seconds it took to complete *task*."""
    task.time_to_complete_seconds = max(0, time_to_complete_seconds)
    await task.save(update_fields=["time_to_complete_seconds"])


async def set_difficulty_rating(task_id: int, user_id: int, rating: int) -> None:
    """Set difficulty_rating on the given task (1-10 scale)."""
    await Task.filter(id=task_id, user_id=user_id).update(difficulty_rating=rating)


async def add_suspicion_reason(task: Task, reason: str) -> None:
    """Append *reason* to task.suspicion_reasons and persist."""
    reasons: list = list(task.suspicion_reasons or [])
    if reason not in reasons:
        reasons.append(reason)
    task.suspicion_reasons = reasons
    await task.save(update_fields=["suspicion_reasons"])


async def count_recent_short_answers(user: User, n: int = 5) -> int:
    """Count how many of the last *n* completed tasks had a check_answer shorter than 6 chars."""
    recent = (
        await Task.filter(user=user, status=TaskStatus.COMPLETED, check_answer__not_isnull=True)
        .order_by("-id")
        .limit(n)
    )
    return sum(1 for t in recent if t.check_answer and len(t.check_answer) < 6)


async def recent_completion_time_deltas(user: User, code: str, k: int = 10) -> list[int]:
    """Return the last *k* time_to_complete_seconds for *code*, oldest first."""
    rows = (
        await Task.filter(
            user=user,
            exercise_code=code,
            status=TaskStatus.COMPLETED,
            time_to_complete_seconds__not_isnull=True,
        )
        .order_by("-id")
        .limit(k)
        .values_list("time_to_complete_seconds", flat=True)
    )
    return list(reversed(rows))


async def recent_difficulty_ratings(user: User, code: str, k: int = 10) -> list[int]:
    """Return the last *k* non-null difficulty ratings for *code*, oldest first."""
    rows = (
        await Task.filter(
            user=user,
            exercise_code=code,
            status=TaskStatus.COMPLETED,
            difficulty_rating__not_isnull=True,
        )
        .order_by("-id")
        .limit(k)
        .values_list("difficulty_rating", flat=True)
    )
    return list(reversed(rows))


async def count_last_n_days(user: User, days: int) -> dict:
    """Return completed/skipped/failed counts over the last *days* days."""
    from datetime import timedelta

    from ..utils.time import today as _today

    cutoff = _today() - timedelta(days=days)
    tasks = await Task.filter(user=user, day__gte=cutoff)
    completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    skipped = sum(1 for t in tasks if t.status == TaskStatus.SKIPPED)
    failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)
    return {"completed": completed, "skipped": skipped, "failed": failed}
