from __future__ import annotations

from datetime import date

from ..db.models import DailyState, User
from ..repositories import daily_states as ds_repo
from ..repositories import tasks as task_repo
from ..repositories import users as user_repo

# Codes that participate in progressive overload / deload
STRENGTH_CORE_CODES = ["squats_easy", "pushups_easy", "abs_crunch", "plank"]
OFFSET_FLOOR = -5

OVERLOAD_PERIOD_DAYS = 14
OVERLOAD_COMPLETION_RATE = 0.8
DELOAD_PERIOD_DAYS = 56  # 8 weeks
DELOAD_COOLDOWN_DAYS = 56


async def maybe_apply_overload(user: User) -> int:
    """Check every 14 days and apply +1 to all strength/core offsets if conditions met.

    Returns count of exercises bumped.
    """
    from ..services.calibration import is_in_baseline

    if is_in_baseline(user):
        return 0

    # Check deload cooldown
    if user.last_deload_at is not None:
        days_since_deload = (date.today() - user.last_deload_at).days
        if days_since_deload < DELOAD_COOLDOWN_DAYS:
            return 0

    counts = await task_repo.count_last_n_days(user, OVERLOAD_PERIOD_DAYS)
    total = counts["completed"] + counts["skipped"] + counts["failed"]
    if total == 0:
        return 0

    rate = counts["completed"] / total
    if rate <= OVERLOAD_COMPLETION_RATE:
        return 0

    bumped = await user_repo.bump_all_offsets(user, STRENGTH_CORE_CODES, +1)
    return bumped


async def maybe_apply_deload(user: User, today: date) -> bool:
    """Every 56 days, reduce all offsets by 3 (floor -5). Returns True if applied."""
    from ..services.calibration import is_in_baseline

    if is_in_baseline(user):
        return False

    if user.last_deload_at is not None:
        days_since = (today - user.last_deload_at).days
        if days_since < DELOAD_PERIOD_DAYS:
            return False
    else:
        # No deload yet — check if enough time has passed since user creation
        days_since_created = (today - user.created_at.date()).days
        if days_since_created < DELOAD_PERIOD_DAYS:
            return False

    # Apply deload: set each offset to max(offset - 3, OFFSET_FLOOR)
    offsets: dict = dict(user.personal_difficulty_offsets or {})
    for code in STRENGTH_CORE_CODES:
        current = int(offsets.get(code, 0))
        offsets[code] = max(OFFSET_FLOOR, current - 3)
    user.personal_difficulty_offsets = offsets
    await user_repo.mark_deload(user, today)
    return True


async def maybe_mark_recovery_day(user: User, today: date, state: DailyState) -> bool:
    """Mark Wednesday (ISO week's 3rd workday) as recovery day. Returns True if marked."""
    if state.recovery_day:
        return False

    # ISO weekday: Monday=1, Tuesday=2, Wednesday=3
    if today.isoweekday() != 3:
        return False

    await ds_repo.mark_recovery_day(state)
    return True
