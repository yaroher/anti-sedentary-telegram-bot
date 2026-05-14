from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject
from loguru import logger

from ..config import settings
from ..services.user import ensure_user


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from_user = getattr(event, "from_user", None)
        if from_user is not None:
            user, is_new_user = await ensure_user(from_user)
            data["user"] = user
            data["is_new_user"] = is_new_user
            with logger.contextualize(user_id=user.user_id):
                return await handler(event, data)
        return await handler(event, data)


class ThrottlingMiddleware(BaseMiddleware):
    """Drop (or answer) events arriving faster than rate_limit_seconds per user+event_type."""

    def __init__(self, rate_limit_seconds: float | None = None) -> None:
        self._rate = rate_limit_seconds if rate_limit_seconds is not None else settings.throttle_rate_seconds
        # {(user_id, event_type): last_seen_monotonic}
        self._last: dict[tuple[int, str], float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from_user = getattr(event, "from_user", None)
        if from_user is not None:
            event_type = type(event).__name__
            key = (from_user.id, event_type)
            now = time.monotonic()
            last = self._last.get(key, 0.0)
            if now - last < self._rate:
                # For callback queries give a brief popup; messages are dropped silently.
                if isinstance(event, CallbackQuery):
                    user = data.get("user")
                    locale = user.language if user is not None else "en"
                    from ..i18n import t

                    await event.answer(t(locale, "throttle.too_fast"))
                return None
            self._last[key] = now
        return await handler(event, data)
