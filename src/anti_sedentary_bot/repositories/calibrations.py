from __future__ import annotations

from ..db.models import ExerciseCalibration, User


async def get(user: User, exercise_code: str) -> ExerciseCalibration | None:
    return await ExerciseCalibration.filter(user=user, exercise_code=exercise_code).first()


async def upsert(
    user: User,
    exercise_code: str,
    completion_seconds: float | None = None,
    difficulty_rating: int | None = None,
) -> ExerciseCalibration:
    """Create or update calibration row. Updates median via running average."""
    cal, _ = await ExerciseCalibration.get_or_create(
        user=user,
        exercise_code=exercise_code,
    )
    if completion_seconds is not None and completion_seconds > 0:
        # Running average for median approximation
        n = cal.sample_count
        cal.median_completion_seconds = (cal.median_completion_seconds * n + completion_seconds) / (n + 1)
        cal.sample_count = n + 1
    if difficulty_rating is not None:
        cal.last_difficulty_rating = difficulty_rating
    await cal.save(
        update_fields=["sample_count", "median_completion_seconds", "last_difficulty_rating", "updated_at"]
    )
    return cal
