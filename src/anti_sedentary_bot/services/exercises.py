from __future__ import annotations

import random

from ..config import settings
from ..db.models import DailyState, User
from ..domain.exercises import EXERCISES, Exercise
from ..repositories import users as user_repo
from ..utils.time import now


def render_instruction(
    exercise: Exercise,
    user: User,
    locale: str,
) -> tuple[str, int, int | None]:
    """Render personalized instruction text.

    Returns (rendered_text, effective_reps_or_zero, effective_seconds_or_None).
    """
    loc = exercise.for_locale(locale)
    offset = user_repo.get_difficulty_offset(user, exercise.code)

    effective_reps = 0
    effective_seconds: int | None = None

    if exercise.base_reps is not None:
        effective_reps = max(1, exercise.base_reps + offset)
    if exercise.base_seconds is not None:
        effective_seconds = max(5, exercise.base_seconds + offset * 5)

    if loc.instruction_template:
        kwargs: dict[str, int] = {}
        if effective_reps:
            kwargs["reps"] = effective_reps
        if effective_seconds is not None:
            kwargs["seconds"] = effective_seconds
        try:
            text = loc.instruction_template.format(**kwargs)
        except (KeyError, IndexError):
            text = loc.instruction
    else:
        text = loc.instruction

    return text, effective_reps, effective_seconds


def choose_exercise(state: DailyState) -> Exercise:
    pool = list(EXERCISES)

    # Recovery day: only mobility exercises
    if getattr(state, "recovery_day", False):
        mobility_pool = [e for e in EXERCISES if e.kind == "mobility"]
        if mobility_pool:
            pool = mobility_pool

    if state.pressure_level >= 2:
        pool += [e for e in pool if e.kind in ("strength", "core")]
    if state.completed_count == 0:
        pool += [e for e in pool if e.kind == "mobility"]

    # Time-of-day weighting
    current_hour = now().astimezone(settings.tz).hour
    if 8 <= current_hour < 12:
        pool += [e for e in pool if e.kind == "mobility"] * 2  # ×3 total
    elif 13 <= current_hour < 16:
        pool += [e for e in pool if e.code == "walk"] * 2  # ×3 total
    elif 17 <= current_hour < 20:
        pool += [e for e in pool if e.kind == "mobility"]  # ×2 total

    return random.choice(pool)
