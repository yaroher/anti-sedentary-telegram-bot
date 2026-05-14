from __future__ import annotations

import asyncio
import random
from datetime import timedelta

from aiogram import Bot

from ..config import settings
from ..db.models import DailyState, MessageRole, Task, User
from ..domain.exercises import Exercise, find_exercise
from ..i18n import t
from ..repositories import busy_periods as busy_repo
from ..repositories import calibrations as cal_repo
from ..repositories import daily_states as ds_repo
from ..repositories import tasks as task_repo
from ..repositories import users as user_repo
from ..utils.time import (
    human_time_left,
    in_quiet_hours,
    in_work_window,
    now,
    today,
    work_window_bounds,
)
from .exercises import choose_exercise, render_instruction
from .llm import add_message, llm_text
from .user import ensure_daily_state, get_daily_state


async def active_task(user: User) -> Task | None:
    return await task_repo.get_active(user)


async def _create_task(user: User, exercise: Exercise) -> Task:
    # Calibrated unlock_seconds
    unlock_seconds = max(
        settings.min_unlock_seconds,
        min(settings.max_unlock_seconds, exercise.unlock_seconds),
    )
    cal = await cal_repo.get(user, exercise.code)
    if cal is not None and cal.sample_count >= 5 and cal.median_completion_seconds > 0:
        calibrated = int(
            min(
                max(cal.median_completion_seconds * 1.2, settings.min_unlock_seconds),
                settings.max_unlock_seconds,
            )
        )
        unlock_seconds = calibrated

    created = now()
    unlock_at = created + timedelta(seconds=unlock_seconds)

    loc = exercise.for_locale(user.language)

    # Render personalized instruction
    rendered_instruction, _eff_reps, _eff_secs = render_instruction(exercise, user, user.language)

    # Check question selection — with small probability use a hard check
    check_question: str | None = None
    if loc.check_questions and random.random() < settings.check_question_probability:
        prob_hard = settings.check_question_probability * 0.3
        if random.random() < prob_hard:
            # Pick a random hard check question
            hard_keys = ["anti_cheat.hard_check_1", "anti_cheat.hard_check_2", "anti_cheat.hard_check_3"]
            key = random.choice(hard_keys)
            hard_q = t(user.language, key)
            # Fall back to normal if key not found
            check_question = hard_q if hard_q != key else random.choice(loc.check_questions)
        else:
            check_question = random.choice(loc.check_questions)

    task = await task_repo.create(
        user=user,
        exercise_code=exercise.code,
        title=loc.title,
        instruction=rendered_instruction,
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
    from . import anti_cheat, calibration

    # Record completion time metrics
    ttc = (now() - task.created_at).total_seconds() - (task.unlock_at - task.created_at).total_seconds()
    ttc = max(0.0, ttc)
    await task_repo.record_completion_metrics(task, ttc)

    await task_repo.mark_completed(task)

    state = await ensure_daily_state(user)
    await ds_repo.bump_completed(state)
    await schedule_next_task(user)

    # Calibration update
    await calibration.update_from_task(user, task)

    # Baseline graduation check
    graduated = await calibration.maybe_graduate_baseline(user)
    if graduated:
        # Will be sent by bot context — return flag via notification
        pass

    # Anti-cheat assessment
    reasons = await anti_cheat.assess_completion(user, task)
    if reasons:
        # Notify anti-cheat follow-up (fire-and-forget — we don't have bot here)
        # Bot context calls this after; see handler
        pass

    return task, state


async def complete_task_with_bot(bot: Bot, user: User, task: Task) -> tuple[Task, DailyState]:
    """Complete task with bot context for notifications."""
    from ..bot.notifications import notify_anti_cheat_followup, notify_simple

    task, state = await complete_task(user, task)

    # Baseline graduation notification
    graduated = (
        user.baseline_completed_at is not None and (now() - user.baseline_completed_at).total_seconds() < 60
    )
    if graduated:
        await notify_simple(bot, user, t(user.language, "baseline.graduation"))

    # Anti-cheat follow-up if suspicious
    if task.suspicious and task.check_question is not None:
        await notify_anti_cheat_followup(bot, user, task)

    # Daily goal reached?
    if state.completed_count >= user.daily_goal and not state.daily_goal_reached:
        await ds_repo.mark_goal_reached(state)
        msg = await llm_text(
            user,
            "daily goal reached",
            {"goal": user.daily_goal},
            fallback=t(user.language, "fallback.goal_reached"),
        )
        goal_text = t(user.language, "goal.reached", msg=msg)
        await notify_simple(bot, user, goal_text)
        await ds_repo.set_next_task_at(state, None)

    return task, state


async def skip_task(user: User, task: Task, hard: bool) -> Task:
    await task_repo.mark_skipped(task)

    state = await ensure_daily_state(user)
    await ds_repo.bump_skipped(state, hard)
    await schedule_next_task(user)
    return task


async def skip_task_with_bot(bot: Bot, user: User, task: Task, hard: bool) -> Task:
    """Skip task with streak insurance check and notification."""
    from ..bot.notifications import notify_simple

    state = await ensure_daily_state(user)
    insurance_available = await user_repo.streak_insurance_available_this_week(user, today())
    used_insurance = insurance_available and state.streak > 0

    if used_insurance:
        # Don't zero streak — use insurance
        await user_repo.use_streak_insurance(user, today())
        await task_repo.mark_skipped(task)
        state.skipped_count += 1
        if not hard:
            state.pressure_level += 1
        await state.save(update_fields=["skipped_count", "pressure_level"])
        await schedule_next_task(user)
        await notify_simple(bot, user, t(user.language, "streak.insurance_used"))
    else:
        await skip_task(user, task, hard)

    if hard:
        await _notify_partner_skip(bot, user, task)
    return task


async def fail_task(user: User, task: Task) -> Task:
    await task_repo.mark_failed(task)

    state = await ensure_daily_state(user)
    await ds_repo.bump_failed(state)
    await schedule_next_task(user)
    return task


async def fail_task_with_bot(bot: Bot, user: User, task: Task) -> Task:
    """Fail task with streak insurance check and notification."""
    from ..bot.notifications import notify_simple

    state = await ensure_daily_state(user)
    insurance_available = await user_repo.streak_insurance_available_this_week(user, today())
    used_insurance = insurance_available and state.streak > 0

    if used_insurance:
        await user_repo.use_streak_insurance(user, today())
        await task_repo.mark_failed(task)
        state.failed_count += 1
        state.pressure_level += 2
        await state.save(update_fields=["failed_count", "pressure_level"])
        await schedule_next_task(user)
        await notify_simple(bot, user, t(user.language, "streak.insurance_used"))
    else:
        await fail_task(user, task)

    return task


async def maybe_nudge_or_fail(bot: Bot, user: User, task: Task) -> None:
    from ..bot.notifications import notify_fail, notify_nudge

    age_minutes = (now() - task.created_at).total_seconds() / 60

    if age_minutes >= settings.fail_after_minutes:
        await fail_task_with_bot(bot, user, task)
        msg = await llm_text(
            user,
            "task failed by neglect",
            {"task": task.title},
            fallback=t(user.language, "fallback.fail"),
        )
        await notify_fail(bot, user, msg)
        await _notify_partner_fail(bot, user, task)
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
            fallback=t(user.language, "fallback.nudge"),
        )
        await notify_nudge(bot, user, task, msg)


async def _tick_user(bot: Bot, user: User, sem: asyncio.Semaphore) -> None:
    from loguru import logger

    from . import progression

    async with sem:
        try:
            state = await ensure_daily_state(user)

            # Check busy period first
            busy = await busy_repo.current(user)
            if busy is not None:
                return

            if not in_work_window(user.day_start, user.day_end):
                return

            # Mark recovery day if applicable
            await progression.maybe_mark_recovery_day(user, today(), state)
            # Re-fetch state after potential update
            state = await ensure_daily_state(user)

            quiet = in_quiet_hours(user.quiet_start, user.quiet_end)

            task = await active_task(user)
            if task:
                if not quiet:
                    await maybe_nudge_or_fail(bot, user, task)
                return

            if quiet:
                return

            # Check daily goal reached
            if state.completed_count >= user.daily_goal:
                if not state.daily_goal_reached:
                    await ds_repo.mark_goal_reached(state)
                return

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
    "complete_task_with_bot",
    "fail_task",
    "fail_task_with_bot",
    "find_exercise",
    "maybe_nudge_or_fail",
    "schedule_next_task",
    "send_task",
    "skip_task",
    "skip_task_with_bot",
    "tick_scheduler",
]


async def _notify_partner_fail(bot: Bot, user: User, task: Task) -> None:
    """Fire-and-forget partner notification — never raises."""
    from ..bot.notifications import notify_simple
    from ..repositories import partnerships as partner_repo

    try:
        partner = await partner_repo.partner_of(user)
        if partner and partner.is_enabled and not partner.is_deleted:
            my_name = user.first_name or user.username or str(user.user_id)
            msg = t(partner.language, "partner.notify_fail", name=my_name, title=task.title)
            await notify_simple(bot, partner, msg)
    except Exception:
        from loguru import logger

        logger.exception("partner notify_fail failed")


async def _notify_partner_skip(bot: Bot, user: User, task: Task) -> None:
    """Fire-and-forget partner notification for hard skip — never raises."""
    from ..bot.notifications import notify_simple
    from ..repositories import partnerships as partner_repo

    try:
        partner = await partner_repo.partner_of(user)
        if partner and partner.is_enabled and not partner.is_deleted:
            my_name = user.first_name or user.username or str(user.user_id)
            msg = t(partner.language, "partner.notify_skip", name=my_name, title=task.title)
            await notify_simple(bot, partner, msg)
    except Exception:
        from loguru import logger

        logger.exception("partner notify_skip failed")
