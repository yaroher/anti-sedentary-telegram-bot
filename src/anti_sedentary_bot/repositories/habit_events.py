from __future__ import annotations

from datetime import datetime

from ..config import settings
from ..db.models import HabitTrackEvent, User
from ..utils.time import now


async def record(user: User, kind: str) -> HabitTrackEvent:
    """Record a single habit acknowledgement event."""
    return await HabitTrackEvent.create(user=user, kind=kind)


async def count_today(user: User, kind: str) -> int:
    """Count habit events of *kind* that occurred today (server/user timezone)."""
    today_date = now().date()
    # created_at is tz-aware; filter by date() equivalent using range
    from datetime import timedelta

    from ..utils.time import now as _now

    _now_dt = _now()
    # Start and end of today in the configured timezone
    day_start = _now_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    return await HabitTrackEvent.filter(
        user=user,
        kind=kind,
        created_at__gte=day_start,
        created_at__lt=day_end,
    ).count()


async def last_event_at(user: User, kind: str) -> datetime | None:
    """Return the created_at timestamp of the most recent event of *kind*, or None."""
    row = await HabitTrackEvent.filter(user=user, kind=kind).order_by("-created_at").first()
    return row.created_at if row is not None else None
