from __future__ import annotations

from datetime import timedelta

from aiogram import Bot
from loguru import logger

from ..bot.notifications import notify_simple
from ..i18n import t
from ..repositories import daily_states as ds_repo
from ..repositories import users as user_repo
from ..services.llm import llm_text
from ..utils.time import now


async def find_dormant_users(days: int = 3) -> list:
    """Return enabled, non-deleted users with no task activity for >= *days* days,
    excluding those re-engaged within last 7 days."""

    candidates = await ds_repo.find_dormant_users(days=days)
    cutoff_reengaged = now() - timedelta(days=7)
    result = []
    for user in candidates:
        if user.reengaged_at is not None and user.reengaged_at >= cutoff_reengaged:
            continue
        result.append(user)
    return result


async def reengage(bot: Bot) -> int:
    """Send one re-engagement message to each dormant user. Returns the count sent."""
    users = await find_dormant_users(days=3)
    sent = 0
    for user in users:
        try:
            # Compute how many days silent
            from ..repositories import daily_states as ds_repo2

            days_states = await ds_repo2.last_n_days(user, 30)
            last_active_days = 0
            for ds in days_states:
                if ds.last_task_at is not None:
                    from ..utils.time import now as _now

                    delta = _now() - ds.last_task_at
                    last_active_days = int(delta.total_seconds() / 86400)
                    break

            msg = await llm_text(
                user,
                "re-engage softly after silence",
                {"days_silent": last_active_days or 3},
            )
            if not msg:
                msg = t(user.language, "reengage.silent")
            await notify_simple(bot, user, msg)
            await user_repo.mark_reengaged(user)
            sent += 1
        except Exception:
            logger.exception("Reengagement error for user_id={}", user.user_id)
    return sent
