from __future__ import annotations

import asyncio
from datetime import timedelta

from aiogram import Bot
from loguru import logger

from ..config import settings
from ..repositories import habit_events as he_repo
from ..repositories import users as user_repo
from ..utils.time import in_quiet_hours, in_work_window, now


async def _should_send(user, kind: str, interval_minutes: int) -> bool:
    """Return True if a health reminder should be sent to user now."""
    if not in_work_window(user.day_start, user.day_end):
        return False
    if in_quiet_hours(user.quiet_start, user.quiet_end):
        return False
    last = await he_repo.last_event_at(user, kind)
    if last is None:
        return True
    return (now() - last) >= timedelta(minutes=interval_minutes)


async def _tick_user_health(bot: Bot, user, kind: str, interval_minutes: int, sem: asyncio.Semaphore) -> None:
    from ..bot.notifications import notify_health

    async with sem:
        try:
            if await _should_send(user, kind, interval_minutes):
                await notify_health(bot, user, kind)
        except Exception:
            logger.exception("Health tick error for user_id={} kind={}", user.user_id, kind)


async def _tick_kind(bot: Bot, kind: str) -> None:
    sem = asyncio.Semaphore(settings.scheduler_concurrency)
    users = await user_repo.list_health_enabled(kind)

    interval_map = {
        "eye": lambda u: u.eye_break_minutes,
        "hydration": lambda u: u.hydration_minutes,
        "posture": lambda u: u.posture_minutes,
    }
    get_interval = interval_map[kind]

    coros = [_tick_user_health(bot, user, kind, get_interval(user), sem) for user in users]
    await asyncio.gather(*coros, return_exceptions=True)


async def tick_eye(bot: Bot) -> None:
    await _tick_kind(bot, "eye")


async def tick_hydration(bot: Bot) -> None:
    await _tick_kind(bot, "hydration")


async def tick_posture(bot: Bot) -> None:
    await _tick_kind(bot, "posture")


__all__ = ["tick_eye", "tick_hydration", "tick_posture"]
