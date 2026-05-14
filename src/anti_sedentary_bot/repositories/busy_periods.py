from __future__ import annotations

from datetime import timedelta

from ..db.models import BusyPeriod, User
from ..utils.time import now


async def create(user: User, ends_at: object, reason: str = "busy") -> BusyPeriod:
    """Create a new busy period starting now and ending at *ends_at*."""
    return await BusyPeriod.create(
        user=user,
        started_at=now(),
        ends_at=ends_at,
        reason=reason,
    )


async def current(user: User) -> BusyPeriod | None:
    """Return the newest active busy period that has not yet expired, or None."""
    _now = now()
    return (
        await BusyPeriod.filter(user=user, ends_at__gt=_now).order_by("-ends_at").first()
    )


async def cleanup_expired() -> int:
    """Delete all expired busy periods (ends_at older than 1 day ago).

    Returns the number of rows deleted.
    """
    cutoff = now() - timedelta(days=1)
    deleted_count, _ = await BusyPeriod.filter(ends_at__lt=cutoff).delete()
    return deleted_count
