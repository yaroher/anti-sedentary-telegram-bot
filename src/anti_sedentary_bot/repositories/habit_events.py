from __future__ import annotations

from datetime import datetime

from ..db.models import HabitTrackEvent, User
from ..utils.time import now


async def record(user: User, kind: str) -> HabitTrackEvent:
    """Record a single habit acknowledgement event."""
    return await HabitTrackEvent.create(user=user, kind=kind)


async def count_today(user: User, kind: str) -> int:
    """Count habit events of *kind* that occurred today (server/user timezone)."""
    from datetime import timedelta

    _now_dt = now()
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
