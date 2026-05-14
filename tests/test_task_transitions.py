"""DB-touching tests for task status transitions and DailyState counter updates."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from anti_sedentary_bot.db.models import DailyState, Task, TaskStatus, User
from anti_sedentary_bot.repositories import daily_states as ds_repo
from anti_sedentary_bot.repositories import tasks as task_repo
from anti_sedentary_bot.services.tasks import complete_task, fail_task, skip_task

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _make_user(user_id: int = 1001) -> User:
    return await User.create(
        user_id=user_id,
        day_start="09:00",
        day_end="17:00",
        break_every_minutes=45,
    )


async def _make_state(user: User) -> DailyState:
    return await ds_repo.get_or_create(user)


async def _make_task(user: User) -> Task:
    now = datetime.now(tz=UTC)
    return await task_repo.create(
        user=user,
        exercise_code="test_exercise",
        title="Test exercise",
        instruction="Do 10 reps.",
        created_at=now,
        unlock_at=now,
        check_question=None,
    )


# ---------------------------------------------------------------------------
# complete_task
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_complete_task_sets_status(tortoise_db: None):
    user = await _make_user(2001)
    task = await _make_task(user)

    await _make_state(user)
    await complete_task(user, task)

    refreshed = await Task.get(id=task.id)
    assert refreshed.status == TaskStatus.COMPLETED
    assert refreshed.completed_at is not None


@pytest.mark.asyncio
async def test_complete_task_increments_completed_count(tortoise_db: None):
    user = await _make_user(2002)
    state = await _make_state(user)
    assert state.completed_count == 0

    task = await _make_task(user)
    _, updated_state = await complete_task(user, task)

    assert updated_state.completed_count == 1


@pytest.mark.asyncio
async def test_complete_task_increments_streak(tortoise_db: None):
    user = await _make_user(2003)
    state = await _make_state(user)
    initial_streak = state.streak

    task = await _make_task(user)
    _, updated_state = await complete_task(user, task)

    assert updated_state.streak == initial_streak + 1


@pytest.mark.asyncio
async def test_complete_task_reduces_pressure(tortoise_db: None):
    user = await _make_user(2004)
    state = await _make_state(user)
    # Manually set pressure_level > 0
    state.pressure_level = 3
    await state.save(update_fields=["pressure_level"])

    task = await _make_task(user)
    _, updated_state = await complete_task(user, task)

    assert updated_state.pressure_level == 2


# ---------------------------------------------------------------------------
# skip_task
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skip_task_sets_status(tortoise_db: None):
    user = await _make_user(3001)
    await _make_state(user)
    task = await _make_task(user)

    await skip_task(user, task, hard=False)

    refreshed = await Task.get(id=task.id)
    assert refreshed.status == TaskStatus.SKIPPED
    assert refreshed.skipped_at is not None


@pytest.mark.asyncio
async def test_skip_task_soft_increments_skipped_and_pressure(tortoise_db: None):
    user = await _make_user(3002)
    state = await _make_state(user)
    assert state.skipped_count == 0
    assert state.pressure_level == 0

    task = await _make_task(user)
    await skip_task(user, task, hard=False)

    refreshed_state = await DailyState.get(id=state.id)
    assert refreshed_state.skipped_count == 1
    assert refreshed_state.pressure_level == 1  # soft skip raises pressure


@pytest.mark.asyncio
async def test_skip_task_hard_does_not_raise_pressure(tortoise_db: None):
    user = await _make_user(3003)
    state = await _make_state(user)

    task = await _make_task(user)
    await skip_task(user, task, hard=True)

    refreshed_state = await DailyState.get(id=state.id)
    assert refreshed_state.skipped_count == 1
    assert refreshed_state.pressure_level == 0  # hard skip keeps pressure


@pytest.mark.asyncio
async def test_skip_task_resets_streak(tortoise_db: None):
    user = await _make_user(3004)
    state = await _make_state(user)
    state.streak = 5
    await state.save(update_fields=["streak"])

    task = await _make_task(user)
    await skip_task(user, task, hard=False)

    refreshed_state = await DailyState.get(id=state.id)
    assert refreshed_state.streak == 0


# ---------------------------------------------------------------------------
# fail_task
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fail_task_sets_status(tortoise_db: None):
    user = await _make_user(4001)
    await _make_state(user)
    task = await _make_task(user)

    await fail_task(user, task)

    refreshed = await Task.get(id=task.id)
    assert refreshed.status == TaskStatus.FAILED
    assert refreshed.failed_at is not None


@pytest.mark.asyncio
async def test_fail_task_increments_failed_and_raises_pressure(tortoise_db: None):
    user = await _make_user(4002)
    state = await _make_state(user)
    assert state.failed_count == 0
    assert state.pressure_level == 0

    task = await _make_task(user)
    await fail_task(user, task)

    refreshed_state = await DailyState.get(id=state.id)
    assert refreshed_state.failed_count == 1
    assert refreshed_state.pressure_level == 2  # fail raises by 2


@pytest.mark.asyncio
async def test_fail_task_resets_streak(tortoise_db: None):
    user = await _make_user(4003)
    state = await _make_state(user)
    state.streak = 10
    await state.save(update_fields=["streak"])

    task = await _make_task(user)
    await fail_task(user, task)

    refreshed_state = await DailyState.get(id=state.id)
    assert refreshed_state.streak == 0
