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
    if state.streak > state.best_streak:
        state.best_streak = state.streak
    await state.save(update_fields=["completed_count", "streak", "pressure_level", "best_streak"])


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


async def mark_goal_reached(state: DailyState) -> None:
    state.daily_goal_reached = True
    await state.save(update_fields=["daily_goal_reached"])


async def mark_recovery_day(state: DailyState) -> None:
    state.recovery_day = True
    await state.save(update_fields=["recovery_day"])


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


async def mark_summary_sent(state: DailyState, when: datetime | None = None) -> None:
    from ..utils.time import now as _now

    state.daily_summary_sent_at = when or _now()
    await state.save(update_fields=["daily_summary_sent_at"])


async def update_best_streak(state: DailyState, value: int) -> None:
    if value > state.best_streak:
        state.best_streak = value
        await state.save(update_fields=["best_streak"])


async def aggregate_week(user: User, weeks_back: int = 0) -> dict:
    """Aggregate completed/skipped/failed/best_streak/days_active over a 7-day window."""
    days = await last_n_days(user, 7 + weeks_back * 7)
    # slice the requested week
    start = weeks_back * 7
    end = start + 7
    window = days[start:end] if len(days) > start else []
    return {
        "completed": sum(d.completed_count for d in window),
        "skipped": sum(d.skipped_count for d in window),
        "failed": sum(d.failed_count for d in window),
        "best_streak": max((d.best_streak for d in window), default=0),
        "days_active": sum(1 for d in window if d.completed_count > 0),
    }


async def completion_heatmap(user: User, days: int = 14) -> dict[int, dict]:
    """Hour-of-day completion heatmap across last *days* days."""
    from ..config import settings
    from ..db.models import Task

    cutoff = (await _utc_now()) - _timedelta(days=days)
    tasks = await Task.filter(user_id=user.user_id, created_at__gte=cutoff).all()
    bucket: dict[int, dict] = {h: {"completed": 0, "skipped": 0, "failed": 0} for h in range(24)}
    for task in tasks:
        for kind, ts in (
            ("completed", task.completed_at),
            ("skipped", task.skipped_at),
            ("failed", task.failed_at),
        ):
            if ts is None:
                continue
            h = ts.astimezone(settings.tz).hour
            bucket[h][kind] += 1
    return bucket


async def _utc_now():
    from ..utils.time import now as _now

    return _now()


from datetime import timedelta as _timedelta  # noqa: E402


async def total_completed(user: User) -> int:
    """Sum of completed_count across all DailyState rows for *user*."""
    from tortoise.functions import Sum

    result = await DailyState.filter(user=user).annotate(total=Sum("completed_count")).values("total")
    if not result:
        return 0
    return int(result[0]["total"] or 0)


async def consecutive_goal_days(user: User, daily_goal: int = 5) -> int:
    """Count consecutive days up to today where completed_count >= daily_goal."""
    from datetime import date as _date
    from datetime import timedelta as _td

    from ..utils.time import today as _today

    cutoff = _today() - _td(days=90)
    rows = (
        await DailyState.filter(user=user, day__gte=cutoff).order_by("-day").values("day", "completed_count")
    )
    count = 0
    expected: _date | None = _today()
    for row in rows:
        if row["day"] != expected:
            break
        if row["completed_count"] < daily_goal:
            break
        count += 1
        expected = row["day"] - _td(days=1)
    return count


async def is_summary_sent_today(state: DailyState) -> bool:
    """Return True if today's daily summary was sent (uses daily_summary_sent_at)."""
    return state.daily_summary_sent_at is not None


async def find_dormant_users(days: int = 3) -> list[User]:
    """Return enabled, non-deleted users with no task activity for >= *days* days."""
    from datetime import timedelta as _td

    from ..utils.time import now as _now

    cutoff = _now() - _td(days=days)
    active_ids_qs = await DailyState.filter(last_task_at__gte=cutoff).values_list("user_id", flat=True)
    active_ids = set(active_ids_qs)
    return await User.filter(is_enabled=True, is_deleted=False).exclude(user_id__in=active_ids)
