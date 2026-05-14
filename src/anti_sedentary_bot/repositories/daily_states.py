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
