from __future__ import annotations

from datetime import datetime, timedelta

from tortoise.exceptions import IntegrityError

from ..db.models import DailyState, User
from ..utils.time import today


async def get_or_create(user: User, day: object | None = None) -> DailyState:
    if day is None:
        day = today()
    try:
        state, _ = await DailyState.get_or_create(user=user, day=day)
    except IntegrityError:
        # Concurrent call already inserted the row; fetch the existing one.
        state = await DailyState.get(user=user, day=day)
    return state


async def bump_completed(state: DailyState) -> None:
    state.completed_count += 1
    state.streak += 1
    if state.pressure_level > 0:
        state.pressure_level -= 1
    await state.save(update_fields=["completed_count", "streak", "pressure_level"])


async def bump_skipped(state: DailyState, hard: bool) -> None:
    state.skipped_count += 1
    state.streak = 0
    if not hard:
        state.pressure_level += 1
    await state.save(update_fields=["skipped_count", "streak", "pressure_level"])


async def bump_failed(state: DailyState) -> None:
    state.failed_count += 1
    state.streak = 0
    state.pressure_level += 2
    await state.save(update_fields=["failed_count", "streak", "pressure_level"])


async def set_next_task_at(state: DailyState, dt: datetime | None) -> None:
    state.next_task_at = dt
    await state.save(update_fields=["next_task_at"])


async def set_last_task_at(state: DailyState, dt: datetime | None) -> None:
    state.last_task_at = dt
    await state.save(update_fields=["last_task_at"])


async def last_n_days(user: User, n: int) -> list[DailyState]:
    """Return up to *n* most recent DailyState rows for *user*, newest first."""
    cutoff = today() - timedelta(days=n)
    return await DailyState.filter(user=user, day__gte=cutoff).order_by("-day")


# ---------------------------------------------------------------------------
# Effectiveness additions
# ---------------------------------------------------------------------------


async def bump_water(state: DailyState) -> DailyState:
    state.water_count += 1
    await state.save(update_fields=["water_count"])
    return state


async def bump_eye_break(state: DailyState) -> DailyState:
    state.eye_breaks_done += 1
    await state.save(update_fields=["eye_breaks_done"])
    return state


async def bump_posture(state: DailyState) -> DailyState:
    state.posture_checks_done += 1
    await state.save(update_fields=["posture_checks_done"])
    return state


async def mark_recovery_day(state: DailyState) -> None:
    state.recovery_day = True
    await state.save(update_fields=["recovery_day"])


async def mark_goal_reached(state: DailyState) -> None:
    state.daily_goal_reached = True
    await state.save(update_fields=["daily_goal_reached"])


async def mark_summary_sent(state: DailyState, when: datetime | None = None) -> None:
    from ..utils.time import now as _now

    state.daily_summary_sent_at = when or _now()
    await state.save(update_fields=["daily_summary_sent_at"])


async def update_best_streak(state: DailyState, value: int) -> None:
    if value > state.best_streak_today:
        state.best_streak_today = value
        await state.save(update_fields=["best_streak_today"])


async def aggregate_week(user: User, weeks_back: int = 0) -> dict:
    """Return aggregated stats for a 7-day window.

    weeks_back=0  → most recent 7 days
    weeks_back=1  → the 7 days before that, etc.
    """
    offset_days = weeks_back * 7
    end = today() - timedelta(days=offset_days)
    start = end - timedelta(days=7)
    rows = await DailyState.filter(user=user, day__gt=start, day__lte=end)
    completed = sum(r.completed_count for r in rows)
    skipped = sum(r.skipped_count for r in rows)
    failed = sum(r.failed_count for r in rows)
    best_streak = max((r.best_streak_today for r in rows), default=0)
    days_active = sum(1 for r in rows if r.completed_count > 0)
    return {
        "completed": completed,
        "skipped": skipped,
        "failed": failed,
        "best_streak": best_streak,
        "days_active": days_active,
    }


async def completion_heatmap(user: User, days: int = 14) -> dict[int, dict]:
    """Return per-hour completion stats over the last *days* days.

    Keys are local-timezone hour integers (0-23).
    Values: {"completed": N, "skipped": M, "failed": K}
    """
    from ..db.models import Task, TaskStatus
    from ..utils.time import to_tz

    cutoff = today() - timedelta(days=days)
    tasks = await Task.filter(user=user, day__gte=cutoff)

    result: dict[int, dict] = {}
    for task in tasks:
        if task.status == TaskStatus.COMPLETED and task.completed_at:
            hour = to_tz(task.completed_at).hour
            bucket = result.setdefault(hour, {"completed": 0, "skipped": 0, "failed": 0})
            bucket["completed"] += 1
        elif task.status == TaskStatus.SKIPPED and task.skipped_at:
            hour = to_tz(task.skipped_at).hour
            bucket = result.setdefault(hour, {"completed": 0, "skipped": 0, "failed": 0})
            bucket["skipped"] += 1
        elif task.status == TaskStatus.FAILED and task.failed_at:
            hour = to_tz(task.failed_at).hour
            bucket = result.setdefault(hour, {"completed": 0, "skipped": 0, "failed": 0})
            bucket["failed"] += 1
    return result
