from __future__ import annotations

from ..db.models import ExerciseCalibration, User

_ALPHA = 0.3  # EMA smoothing factor


async def upsert(
    user: User,
    exercise_code: str,
    completion_seconds: int | None,
    difficulty: int | None,
) -> ExerciseCalibration:
    """Update rolling calibration estimates for *user* / *exercise_code*.

    Uses an exponential moving average (alpha=0.3) as a good-enough rolling
    median estimate without maintaining sorted buffers.
    """
    cal, _ = await ExerciseCalibration.get_or_create(user=user, exercise_code=exercise_code)
    cal.sample_count += 1

    if completion_seconds is not None:
        if cal.sample_count == 1:
            cal.median_completion_seconds = max(0, completion_seconds)
        else:
            cal.median_completion_seconds = int(
                _ALPHA * completion_seconds + (1 - _ALPHA) * cal.median_completion_seconds
            )

    if difficulty is not None:
        if cal.sample_count == 1:
            cal.median_difficulty = float(difficulty)
        else:
            cal.median_difficulty = _ALPHA * difficulty + (1 - _ALPHA) * cal.median_difficulty

    await cal.save(
        update_fields=["sample_count", "median_completion_seconds", "median_difficulty"]
    )
    return cal


async def get(user: User, exercise_code: str) -> ExerciseCalibration | None:
    """Return the calibration record for *user* / *exercise_code*, or None."""
    return await ExerciseCalibration.filter(user=user, exercise_code=exercise_code).first()
