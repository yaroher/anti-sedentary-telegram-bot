from __future__ import annotations

import asyncio
import random
from datetime import timedelta

from aiogram import Bot

from ..config import settings
from ..db.models import DailyState, MessageRole, Task, User
from ..domain.exercises import Exercise, find_exercise
from ..i18n import t
from ..repositories import daily_states as ds_repo
from ..repositories import tasks as task_repo
from ..repositories import users as user_repo
from ..utils.time import (
    human_time_left,
    in_quiet_hours,
    in_work_window,
    now,
    work_window_bounds,
)
from .exercises import choose_exercise
from .llm import add_message, llm_text
from .user import ensure_daily_state, get_daily_state


async def active_task(user: User) -> Task | None:
    return await task_repo.get_active(user)


async def _create_task(user: User, exercise: Exercise) -> Task:
    unlock_seconds = max(
        settings.min_unlock_seconds,
        min(settings.max_unlock_seconds, exercise.unlock_seconds),
    )
    created = now()
    unlock_at = created + timedelta(seconds=unlock_seconds)

    loc = exercise.for_locale(user.language)
    check_question: str | None = None
    if loc.check_questions and random.random() < settings.check_question_probability:
        check_question = random.choice(loc.check_questions)

    task = await task_repo.create(
        user=user,
        exercise_code=exercise.code,
        title=loc.title,
        instruction=loc.instruction,
        unlock_at=unlock_at,
        created_at=created,
        check_question=check_question,
    )
    state = await ensure_daily_state(user)
    await ds_repo.set_last_task_at(state, created)
    await ds_repo.set_next_task_at(state, None)
    return task


async def schedule_next_task(user: User) -> None:
    start_dt, end_dt = work_window_bounds(user.day_start, user.day_end)
    candidate = now() + timedelta(minutes=user.break_every_minutes)
    if candidate < start_dt:
        candidate = start_dt
    if candidate > end_dt:
        candidate = start_dt + timedelta(days=1)
    state = await ensure_daily_state(user)
    await ds_repo.set_next_task_at(state, candidate)


async def send_task(bot: Bot, user: User, reason: str = "scheduled") -> None:
    from ..bot.notifications import notify_new_task

    if await active_task(user):
        return
    state = await get_daily_state(user)
    exercise = choose_exercise(state)
    task = await _create_task(user, exercise)
    unlock_seconds = int((task.unlock_at - task.created_at).total_seconds())

    intro = await llm_text(
        user,
        "issue a new task",
        {
            "reason": reason,
            "exercise": task.title,
            "instruction": task.instruction,
            "unlock_seconds": unlock_seconds,
            "pressure_level": state.pressure_level,
        },
    )

    text = t(
        user.language,
        "task.body",
        intro=intro,
        title=task.title,
        instruction=task.instruction,
        left=human_time_left(task.unlock_at),
    )
    await add_message(user, MessageRole.ASSISTANT, text)
    await notify_new_task(bot, user, task, text)


async def complete_task(user: User, task: Task) -> tuple[Task, DailyState]:
    await task_repo.mark_completed(task)

    state = await ensure_daily_state(user)
    await ds_repo.bump_completed(state)
    await schedule_next_task(user)
    return task, state


async def skip_task(user: User, task: Task, hard: bool) -> Task:
    await task_repo.mark_skipped(task)

    state = await ensure_daily_state(user)
    await ds_repo.bump_skipped(state, hard)
    await schedule_next_task(user)
    return task


async def fail_task(user: User, task: Task) -> Task:
    await task_repo.mark_failed(task)

    state = await ensure_daily_state(user)
    await ds_repo.bump_failed(state)
    await schedule_next_task(user)
    return task


async def maybe_nudge_or_fail(bot: Bot, user: User, task: Task) -> None:
    from ..bot.notifications import notify_fail, notify_nudge

    age_minutes = (now() - task.created_at).total_seconds() / 60

    if age_minutes >= settings.fail_after_minutes:
        await fail_task(user, task)
        msg = await llm_text(user, "task failed by neglect", {"task": task.title})
        await notify_fail(bot, user, msg)
        return

    threshold = settings.nudge_after_minutes * (task.nudge_count + 1)
    if age_minutes >= threshold and task.nudge_count < settings.max_nudges_before_penalty:
        await task_repo.bump_nudge(task)
        msg = await llm_text(
            user,
            "remind about active task",
            {
                "task": task.title,
                "instruction": task.instruction,
                "nudge_count": task.nudge_count,
            },
        )
        await notify_nudge(bot, user, task, msg)


async def _tick_user(bot: Bot, user: User, sem: asyncio.Semaphore) -> None:
    from loguru import logger

    async with sem:
        try:
            await ensure_daily_state(user)

            if not in_work_window(user.day_start, user.day_end):
                return

            quiet = in_quiet_hours(user.quiet_start, user.quiet_end)

            task = await active_task(user)
            if task:
                # During quiet hours, skip nudge/fail logic entirely — just wait.
                if not quiet:
                    await maybe_nudge_or_fail(bot, user, task)
                return

            # Don't send new tasks during quiet hours.
            if quiet:
                return

            state = await get_daily_state(user)
            if state.next_task_at is None:
                await ds_repo.set_next_task_at(state, now() + timedelta(minutes=2))
                return

            if now() >= state.next_task_at:
                await send_task(bot, user, reason="scheduled")
        except Exception:
            logger.exception("Scheduler tick error for user_id={}", user.user_id)


async def tick_scheduler(bot: Bot) -> None:
    sem = asyncio.Semaphore(settings.scheduler_concurrency)
    users = await user_repo.list_enabled()
    coros = [_tick_user(bot, user, sem) for user in users]
    await asyncio.gather(*coros, return_exceptions=True)


__all__ = [
    "active_task",
    "complete_task",
    "fail_task",
    "find_exercise",
    "maybe_nudge_or_fail",
    "schedule_next_task",
    "send_task",
    "skip_task",
    "tick_scheduler",
]
