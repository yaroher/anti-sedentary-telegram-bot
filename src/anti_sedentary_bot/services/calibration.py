from __future__ import annotations

from ..db.models import Task, User
from ..repositories import calibrations as cal_repo
from ..repositories import tasks as task_repo
from ..repositories import users as user_repo
from ..utils.time import now

# Codes considered "strength/core" for baseline penalty
STRENGTH_CODES = {"squats_easy", "pushups_easy", "abs_crunch", "plank"}

BASELINE_MIN_TASKS = 10
BASELINE_MIN_DAYS = 5


async def maybe_init_baseline(user: User) -> None:
    """Initialize baseline offsets for a new user (call once at creation)."""
    if user.baseline_completed_at is not None:
        return
    strength_codes = list(STRENGTH_CODES)
    await user_repo.init_baseline_offsets(user, strength_codes)


async def update_from_task(user: User, task: Task) -> None:
    """Update calibration data from a completed task."""
    completion_secs = task.time_to_complete_seconds
    rating = task.difficulty_rating
    await cal_repo.upsert(
        user=user,
        exercise_code=task.exercise_code,
        completion_seconds=completion_secs,
        difficulty_rating=rating,
    )


async def apply_difficulty_rating(user: User, task: Task) -> None:
    """Adjust personal offset based on difficulty rating (1-10).

    Called after a rating is parsed from check_answer.
    """
    rating = task.difficulty_rating
    if rating is None:
        return
    if rating <= 3:
        await user_repo.set_difficulty_offset(user, task.exercise_code, +1)
    elif rating >= 8:
        await user_repo.set_difficulty_offset(user, task.exercise_code, -1)
    # Update calibration record with the rating
    await cal_repo.upsert(user=user, exercise_code=task.exercise_code, difficulty_rating=rating)


async def maybe_graduate_baseline(user: User) -> bool:
    """Check if baseline phase should end. Returns True if just graduated."""
    if user.baseline_completed_at is not None:
        return False

    total_completed = await task_repo.count_all_completed(user)
    if total_completed < BASELINE_MIN_TASKS:
        return False

    days_since_created = (now() - user.created_at).days
    if days_since_created < BASELINE_MIN_DAYS:
        return False

    await user_repo.mark_baseline_completed(user, now())
    return True


def is_in_baseline(user: User) -> bool:
    """Return True if user is still in the baseline calibration phase."""
    return user.baseline_completed_at is None
