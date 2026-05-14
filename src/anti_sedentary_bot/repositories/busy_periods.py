from __future__ import annotations

from ..db.models import BusyPeriod, User
from ..utils.time import now


async def create(user: User, reason: str, ends_at: object) -> BusyPeriod:
    return await BusyPeriod.create(user=user, reason=reason, ends_at=ends_at)


async def current(user: User) -> BusyPeriod | None:
    """Return the currently active busy period for a user, if any."""
    return await BusyPeriod.filter(user=user, ends_at__gt=now()).order_by("-ends_at").first()


async def cleanup_expired(grace_days: int = 1) -> int:
    """Delete rows whose ends_at is older than now - grace_days. Returns count."""
    from datetime import timedelta

    cutoff = now() - timedelta(days=grace_days)
    deleted, _ = await BusyPeriod.filter(ends_at__lt=cutoff).delete()
    return int(deleted)
