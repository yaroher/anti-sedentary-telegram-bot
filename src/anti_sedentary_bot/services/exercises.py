from __future__ import annotations

import random

from ..db.models import DailyState
from ..domain.exercises import EXERCISES, Exercise


def choose_exercise(state: DailyState) -> Exercise:
    pool = list(EXERCISES)
    if state.pressure_level >= 2:
        pool += [e for e in EXERCISES if e.kind in ("strength", "core")]
    if state.completed_count == 0:
        pool += [e for e in EXERCISES if e.kind == "mobility"]
    return random.choice(pool)
