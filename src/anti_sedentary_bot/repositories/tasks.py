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


async def record_completion_metrics(task: Task, time_to_complete_seconds: float) -> None:
    """Save completion time metrics."""
    task.time_to_complete_seconds = max(0.0, time_to_complete_seconds)
    await task.save(update_fields=["time_to_complete_seconds"])


async def set_difficulty_rating(task_id: int, user_id: int, rating: int) -> None:
    """Save a self-reported difficulty rating (1-10)."""
    await Task.filter(id=task_id, user_id=user_id).update(difficulty_rating=rating)


async def add_suspicion_reason(task: Task, reason: str) -> None:
    """Append a suspicion reason and mark task as suspicious."""
    reasons: list = list(task.suspicion_reasons or [])
    if reason not in reasons:
        reasons.append(reason)
    task.suspicion_reasons = reasons
    task.suspicious = True
    await task.save(update_fields=["suspicion_reasons", "suspicious"])


async def last_check_answer_for(user: User, exclude_task_id: int) -> str | None:
    """Return the most recent check_answer for a user, excluding the given task."""
    task = (
        await Task.filter(
            user=user,
            check_answer__not_isnull=True,
        )
        .exclude(id=exclude_task_id)
        .order_by("-id")
        .first()
    )
    if task and task.check_answer:
        return task.check_answer
    return None


async def recent_completion_time_deltas(user: User, code: str, n: int = 5) -> list[float]:
    """Return time_to_complete_seconds for the last n completed tasks of given exercise."""
    tasks = (
        await Task.filter(
            user=user,
            exercise_code=code,
            status=TaskStatus.COMPLETED,
            time_to_complete_seconds__not_isnull=True,
        )
        .order_by("-id")
        .limit(n)
    )
    return [t.time_to_complete_seconds for t in tasks if t.time_to_complete_seconds is not None]


async def count_recent_short_answers(user: User, n: int) -> int:
    """Count how many of the last n completed tasks have short check_answers."""
    tasks = (
        await Task.filter(user=user, status=TaskStatus.COMPLETED, check_answer__not_isnull=True)
        .order_by("-id")
        .limit(n)
    )
    return sum(1 for t in tasks if t.check_answer and len(t.check_answer.strip()) < 6)


async def count_last_n_days(user: User, days: int) -> dict[str, int]:
    """Return counts of completed/skipped/failed tasks in the last N days."""

    from ..utils.time import today as _today

    cutoff = _today() - timedelta(days=days)
    tasks = await Task.filter(user=user, day__gte=cutoff).exclude(status=TaskStatus.ACTIVE)
    result = {"completed": 0, "skipped": 0, "failed": 0, "total": 0}
    for t in tasks:
        result["total"] += 1
        if t.status == TaskStatus.COMPLETED:
            result["completed"] += 1
        elif t.status == TaskStatus.SKIPPED:
            result["skipped"] += 1
        elif t.status == TaskStatus.FAILED:
            result["failed"] += 1
    return result


async def count_all_completed(user: User) -> int:
    """Return total number of completed tasks for user."""
    return await Task.filter(user=user, status=TaskStatus.COMPLETED).count()


async def completed_in_window(user: User, since) -> list[tuple]:
    rows = await Task.filter(
        user=user,
        status=TaskStatus.COMPLETED,
        completed_at__gte=since,
        completed_at__isnull=False,
    ).values_list("completed_at", "exercise_code")
    return list(rows)


async def failed_skipped_in_window(user: User, since) -> list:
    rows = await Task.filter(
        user=user,
        status__in=[TaskStatus.SKIPPED, TaskStatus.FAILED],
        created_at__gte=since,
    ).values_list("created_at", flat=True)
    return list(rows)


async def count_early_completions(user: User, before_hour: int = 10) -> int:
    """Count distinct days with a completion before *before_hour* local time."""
    from ..utils.time import to_tz

    completed = await Task.filter(
        user=user,
        status=TaskStatus.COMPLETED,
        completed_at__isnull=False,
    ).values_list("completed_at", flat=True)
    days_set: set = set()
    for ts in completed:
        local = to_tz(ts)
        if local.hour < before_hour:
            days_set.add(local.date())
    return len(days_set)


async def count_late_completions(user: User, from_hour: int = 18) -> int:
    from ..utils.time import to_tz

    completed = await Task.filter(
        user=user,
        status=TaskStatus.COMPLETED,
        completed_at__isnull=False,
    ).values_list("completed_at", flat=True)
    days_set: set = set()
    for ts in completed:
        local = to_tz(ts)
        if local.hour >= from_hour:
            days_set.add(local.date())
    return len(days_set)


async def recent_completions_by_code(user: User, exercise_code: str, limit: int = 10) -> list:
    return (
        await Task.filter(user=user, exercise_code=exercise_code, status=TaskStatus.COMPLETED)
        .order_by("-completed_at")
        .limit(limit)
    )
