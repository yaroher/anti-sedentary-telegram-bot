from __future__ import annotations

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from ..config import settings
from .cleanup import run_message_cleanup
from .daily_summary import send_daily_summary
from .memory_bank import refresh_all_users
from .reengagement import reengage
from .summary import send_weekly_summary
from .tasks import tick_scheduler


def build_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.tz)

    scheduler.add_job(
        tick_scheduler,
        IntervalTrigger(seconds=settings.scheduler_tick_seconds),
        kwargs={"bot": bot},
        id="tick",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    scheduler.add_job(
        run_message_cleanup,
        CronTrigger(hour=settings.cleanup_hour, minute=0, timezone=settings.tz),
        id="cleanup",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    scheduler.add_job(
        send_weekly_summary,
        CronTrigger(
            day_of_week=settings.weekly_summary_day_of_week,
            hour=settings.weekly_summary_hour,
            minute=0,
            timezone=settings.tz,
        ),
        kwargs={"bot": bot},
        id="weekly_summary",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    # Daily summary — hourly at :05, per-user end-of-day check inside
    scheduler.add_job(
        send_daily_summary,
        CronTrigger(minute=5, timezone=settings.tz),
        kwargs={"bot": bot},
        id="daily_summary",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    # Re-engagement — daily at 11:00
    scheduler.add_job(
        reengage,
        CronTrigger(hour=11, minute=0, timezone=settings.tz),
        kwargs={"bot": bot},
        id="reengage",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    # LLM memory bank — weekly Sunday at 22:00
    scheduler.add_job(
        refresh_all_users,
        CronTrigger(day_of_week="sun", hour=22, minute=0, timezone=settings.tz),
        kwargs={"bot": bot},
        id="memory_bank",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    logger.info(
        "Scheduler built: tick={}s, cleanup at {:02d}:00 {}",
        settings.scheduler_tick_seconds,
        settings.cleanup_hour,
        settings.timezone,
    )
    return scheduler
