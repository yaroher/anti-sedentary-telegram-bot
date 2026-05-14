from __future__ import annotations

from ..db.models import Achievement, User


async def award(user: User, code: str) -> tuple[Achievement, bool]:
    """Get or create an achievement for *user* with *code*.

    Returns (row, created) — created is True only when the achievement was
    freshly inserted.
    """
    achievement, created = await Achievement.get_or_create(user=user, code=code)
    return achievement, created


async def has(user: User, code: str) -> bool:
    """Return True if *user* already has the achievement *code*."""
    return await Achievement.filter(user=user, code=code).exists()


async def list_for_user(user: User) -> list[Achievement]:
    """Return all achievements for *user*, oldest first."""
    return await Achievement.filter(user=user).order_by("awarded_at")
