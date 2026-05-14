from __future__ import annotations

from datetime import UTC, datetime

from aiogram.types import User as TgUser
from loguru import logger
from tortoise.exceptions import IntegrityError

from ..config import settings
from ..db.models import User
from ..i18n import normalize_locale


async def get_or_create_from_tg(tg_user: TgUser) -> tuple[User, bool]:
    """Get or create a User from a Telegram user object. Returns (user, created)."""
    try:
        user, created = await User.get_or_create(
            user_id=tg_user.id,
            defaults={
                "username": tg_user.username,
                "first_name": tg_user.first_name,
                "language": normalize_locale(tg_user.language_code),
                "day_start": settings.default_day_start,
                "day_end": settings.default_day_end,
                "break_every_minutes": settings.default_break_every_minutes,
            },
        )
    except IntegrityError:
        # Concurrent /start — fetch the row that the other request inserted.
        user = await User.get(user_id=tg_user.id)
        created = False

    if not created:
        if user.is_deleted:
            logger.info("Returning deleted user {} — restoring account", tg_user.id)
            user.is_deleted = False
            user.deleted_at = None
            await user.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
        await update_profile(user, tg_user.username, tg_user.first_name)

    return user, created


async def update_profile(
    user: User,
    username: str | None,
    first_name: str | None,
) -> None:
    dirty = False
    if user.username != username:
        user.username = username
        dirty = True
    if user.first_name != first_name:
        user.first_name = first_name
        dirty = True
    if dirty:
        await user.save(update_fields=["username", "first_name", "updated_at"])


async def set_language(user: User, code: str) -> None:
    user.language = code
    await user.save(update_fields=["language", "updated_at"])


async def set_flavor(user: User, key: str) -> None:
    user.flavor = key
    await user.save(update_fields=["flavor", "updated_at"])


async def set_schedule(user: User, day_start: str, day_end: str) -> None:
    user.day_start = day_start
    user.day_end = day_end
    await user.save(update_fields=["day_start", "day_end", "updated_at"])


async def set_interval(user: User, minutes: int) -> None:
    user.break_every_minutes = minutes
    await user.save(update_fields=["break_every_minutes", "updated_at"])


async def set_enabled(user: User, enabled: bool) -> None:
    user.is_enabled = enabled
    await user.save(update_fields=["is_enabled", "updated_at"])


async def list_enabled() -> list[User]:
    return await User.filter(is_enabled=True, is_deleted=False)


async def set_quiet_hours(user: User, start: str | None, end: str | None) -> None:
    user.quiet_start = start
    user.quiet_end = end
    await user.save(update_fields=["quiet_start", "quiet_end", "updated_at"])


async def soft_delete(user: User) -> None:
    user.is_deleted = True
    user.deleted_at = datetime.now(tz=UTC)
    await user.save(update_fields=["is_deleted", "deleted_at", "updated_at"])


async def restore(user: User) -> None:
    user.is_deleted = False
    user.deleted_at = None
    await user.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
