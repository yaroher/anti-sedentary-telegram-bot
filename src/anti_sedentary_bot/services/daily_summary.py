from __future__ import annotations

from datetime import timedelta

from aiogram import Bot
from loguru import logger

from ..bot.notifications import notify_simple
from ..i18n import t
from ..repositories import daily_states as ds_repo
from ..repositories import users as user_repo
from ..utils.time import now, parse_hhmm


async def send_daily_summary(bot: Bot) -> None:
    """Send a daily summary to every eligible enabled user."""
    users = await user_repo.list_enabled()
    now_local = now()

    for user in users:
        try:
            day_end = parse_hhmm(user.day_end)
            day_end_dt = now_local.replace(hour=day_end.hour, minute=day_end.minute, second=0, microsecond=0)
            # Only send if current time is >= day_end + 5 min
            if now_local < day_end_dt + timedelta(minutes=5):
                continue

            state = await ds_repo.get_or_create(user)

            # Skip if already sent today
            if await ds_repo.is_summary_sent_today(state):
                continue

            # Skip users with zero activity today
            activity = state.completed_count + state.skipped_count + state.failed_count
            if activity == 0:
                continue

            # Build goal status
            daily_goal = 5  # sensible default; could be a user field later
            if state.completed_count >= daily_goal:
                goal_status = t(user.language, "summary.goal_yes")
            else:
                goal_status = t(user.language, "summary.goal_no")

            # Get best_streak across last 30 days
            recent = await ds_repo.last_n_days(user, 30)
            best_streak = max((d.streak for d in recent), default=state.streak)

            text = t(
                user.language,
                "summary.daily",
                completed=state.completed_count,
                skipped=state.skipped_count,
                failed=state.failed_count,
                streak=state.streak,
                best_streak=best_streak,
                goal_status=goal_status,
            )
            await notify_simple(bot, user, text)
            await ds_repo.mark_summary_sent(state)
        except Exception:
            logger.exception("Daily summary error for user_id={}", user.user_id)
