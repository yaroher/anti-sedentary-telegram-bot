from __future__ import annotations

from datetime import UTC, date, datetime

from aiogram.types import User as TgUser
from loguru import logger
from tortoise.exceptions import IntegrityError

from ..config import settings
from ..db.models import User
from ..i18n import normalize_locale

OFFSET_MIN = -5
OFFSET_MAX = 10


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


async def set_daily_goal(user: User, goal: int) -> None:
    user.daily_goal = goal
    await user.save(update_fields=["daily_goal", "updated_at"])


def get_difficulty_offset(user: User, exercise_code: str) -> int:
    """Return the current difficulty offset for a given exercise code (default 0)."""
    offsets: dict = user.personal_difficulty_offsets or {}
    return int(offsets.get(exercise_code, 0))


async def set_difficulty_offset(user: User, exercise_code: str, delta: int) -> int:
    """Apply a relative delta to the difficulty offset and persist. Returns new offset."""
    offsets: dict = dict(user.personal_difficulty_offsets or {})
    current = int(offsets.get(exercise_code, 0))
    new_val = max(OFFSET_MIN, min(OFFSET_MAX, current + delta))
    offsets[exercise_code] = new_val
    user.personal_difficulty_offsets = offsets
    await user.save(update_fields=["personal_difficulty_offsets", "updated_at"])
    return new_val


async def init_baseline_offsets(user: User, codes: list[str]) -> None:
    """Set baseline offset of -2 for strength/core exercises if not already set."""
    offsets: dict = dict(user.personal_difficulty_offsets or {})
    changed = False
    for code in codes:
        if code not in offsets:
            offsets[code] = -2
            changed = True
    if changed:
        user.personal_difficulty_offsets = offsets
        await user.save(update_fields=["personal_difficulty_offsets", "updated_at"])


async def mark_baseline_completed(user: User, when: datetime) -> None:
    user.baseline_completed_at = when
    await user.save(update_fields=["baseline_completed_at", "updated_at"])


async def mark_deload(user: User, today: date) -> None:
    user.last_deload_at = today
    await user.save(update_fields=["last_deload_at", "updated_at"])


async def bump_all_offsets(user: User, codes: list[str], delta: int) -> int:
    """Bump offsets for given codes by delta (clamped). Returns number changed."""
    offsets: dict = dict(user.personal_difficulty_offsets or {})
    changed = 0
    for code in codes:
        current = int(offsets.get(code, 0))
        new_val = max(OFFSET_MIN, min(OFFSET_MAX, current + delta))
        if new_val != current:
            offsets[code] = new_val
            changed += 1
    user.personal_difficulty_offsets = offsets
    await user.save(update_fields=["personal_difficulty_offsets", "updated_at"])
    return changed


async def streak_insurance_available_this_week(user: User, today: date) -> bool:
    """Check if streak insurance is available this ISO week."""
    iso = today.isocalendar()
    week_str = f"{iso.year}-W{iso.week:02d}"
    return user.streak_insurance_used_week != week_str


async def use_streak_insurance(user: User, today: date) -> None:
    """Mark streak insurance as used for this ISO week."""
    iso = today.isocalendar()
    week_str = f"{iso.year}-W{iso.week:02d}"
    user.streak_insurance_used_week = week_str
    await user.save(update_fields=["streak_insurance_used_week", "updated_at"])


async def find_by_username(username: str) -> User | None:
    """Find a user by Telegram username (case-insensitive, without leading @)."""
    clean = username.lstrip("@").lower()
    return await User.filter(username__iexact=clean, is_deleted=False).first()


async def set_health_track(
    user: User,
    kind: str,
    enabled: bool,
    minutes: int | None = None,
) -> None:
    """Toggle eye / hydration / posture tracking. kind in {"eye","hydration","posture"}."""
    kind_map = {
        "eye": ("eye_break_enabled", "eye_break_minutes"),
        "hydration": ("hydration_enabled", "hydration_minutes"),
        "posture": ("posture_enabled", "posture_minutes"),
    }
    if kind not in kind_map:
        raise ValueError(f"Unknown health track kind: {kind!r}")
    enabled_field, minutes_field = kind_map[kind]
    setattr(user, enabled_field, enabled)
    update_fields = [enabled_field, "updated_at"]
    if minutes is not None:
        setattr(user, minutes_field, minutes)
        update_fields.append(minutes_field)
    await user.save(update_fields=update_fields)


async def update_user_facts(user: User, facts_text: str) -> None:
    user.user_facts = facts_text
    await user.save(update_fields=["user_facts", "updated_at"])


async def mark_reengaged(user: User, when: datetime | None = None) -> None:
    """Record that a re-engagement message was sent."""
    user.reengaged_at = when or datetime.now(tz=UTC)
    await user.save(update_fields=["reengaged_at", "updated_at"])


async def list_dormant_for_reengagement(days_silent: int, cooldown_days: int = 7) -> list[User]:
    """Return enabled, non-deleted users with no task activity in *days_silent* days
    and no re-engagement message in the last *cooldown_days* days."""
    from datetime import timedelta

    cutoff_activity = datetime.now(tz=UTC) - timedelta(days=days_silent)
    cutoff_reengage = datetime.now(tz=UTC) - timedelta(days=cooldown_days)
    candidates = await User.filter(is_enabled=True, is_deleted=False).all()
    result: list[User] = []
    for u in candidates:
        if u.reengaged_at is not None and u.reengaged_at > cutoff_reengage:
            continue
        # Lazy import to avoid circular
        from ..db.models import DailyState

        latest = await DailyState.filter(user_id=u.user_id).order_by("-day").first()
        if latest is None or latest.last_task_at is None or latest.last_task_at < cutoff_activity:
            result.append(u)
    return result
