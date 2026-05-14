from __future__ import annotations

from aiogram import Bot
from loguru import logger

from ..bot.retry import safe_send
from ..i18n import t
from ..repositories import daily_states as ds_repo
from ..repositories import users as user_repo


async def send_weekly_summary(bot: Bot) -> None:
    """Send a weekly summary to every enabled user."""
    users = await user_repo.list_enabled()
    for user in users:
        try:
            days = await ds_repo.last_n_days(user, 7)
            completed = sum(d.completed_count for d in days)
            skipped = sum(d.skipped_count for d in days)
            failed = sum(d.failed_count for d in days)
            best_streak = max((d.streak for d in days), default=0)

            text = t(
                user.language,
                "summary.weekly",
                completed=completed,
                skipped=skipped,
                failed=failed,
                best_streak=best_streak,
            )
            await safe_send(lambda uid=user.user_id, txt=text: bot.send_message(uid, txt))
        except Exception:
            logger.exception("Weekly summary error for user_id={}", user.user_id)
