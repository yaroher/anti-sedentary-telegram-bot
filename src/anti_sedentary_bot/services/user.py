from __future__ import annotations

from aiogram.types import User as TgUser

from ..db.models import DailyState, User
from ..repositories import daily_states as ds_repo
from ..repositories import users as user_repo


async def ensure_user(tg_user: TgUser) -> tuple[User, bool]:
    """Returns (user, created). Used by UserMiddleware."""
    user, created = await user_repo.get_or_create_from_tg(tg_user)
    await ensure_daily_state(user)
    return user, created


async def ensure_daily_state(user: User) -> DailyState:
    return await ds_repo.get_or_create(user)


async def get_daily_state(user: User) -> DailyState:
    return await ensure_daily_state(user)
