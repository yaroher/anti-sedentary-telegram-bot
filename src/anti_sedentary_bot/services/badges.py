from __future__ import annotations

from loguru import logger

from ..db.models import DailyState, User
from ..repositories import achievements as ach_repo
from ..repositories import daily_states as ds_repo
from ..repositories import tasks as task_repo

# ---------------------------------------------------------------------------
# Badge code constants
# ---------------------------------------------------------------------------

STREAK_3 = "streak_3"
STREAK_7 = "streak_7"
STREAK_30 = "streak_30"
STREAK_100 = "streak_100"

COMPLETED_50 = "completed_50"
COMPLETED_200 = "completed_200"
COMPLETED_1000 = "completed_1000"

EARLY_BIRD = "early_bird"
NIGHT_OWL = "night_owl"

GOAL_STREAK_7 = "goal_streak_7"

# Minimum daily completions to be counted as "goal reached" for goal_streak_7
_DAILY_GOAL = 5
# Minimum distinct days for early/night_owl
_HOURS_THRESHOLD = 5


async def check_for_user(user: User, state: DailyState | None = None) -> list[str]:
    """Check all badge rules for *user* and award any newly earned ones.

    Returns a list of badge codes that were *newly* awarded in this call.
    """
    if state is None:
        state = await ds_repo.get_or_create(user)

    newly_awarded: list[str] = []

    async def _try(code: str, eligible: bool) -> None:
        if eligible:
            created = await ach_repo.award(user, code)
            if created:
                newly_awarded.append(code)

    # --- streak badges ---
    streak = state.streak
    await _try(STREAK_3, streak >= 3)
    await _try(STREAK_7, streak >= 7)
    await _try(STREAK_30, streak >= 30)
    await _try(STREAK_100, streak >= 100)

    # --- total completions ---
    total = await ds_repo.total_completed(user)
    await _try(COMPLETED_50, total >= 50)
    await _try(COMPLETED_200, total >= 200)
    await _try(COMPLETED_1000, total >= 1000)

    # --- early bird / night owl ---
    early_days = await task_repo.count_early_completions(user, before_hour=10)
    await _try(EARLY_BIRD, early_days >= _HOURS_THRESHOLD)

    late_days = await task_repo.count_late_completions(user, from_hour=18)
    await _try(NIGHT_OWL, late_days >= _HOURS_THRESHOLD)

    # --- goal streak ---
    goal_streak = await ds_repo.consecutive_goal_days(user, daily_goal=_DAILY_GOAL)
    await _try(GOAL_STREAK_7, goal_streak >= 7)

    if newly_awarded:
        logger.info("Badges awarded to user_id={}: {}", user.user_id, newly_awarded)

    return newly_awarded
