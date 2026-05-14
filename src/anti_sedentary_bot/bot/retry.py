from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from aiogram.exceptions import (
    TelegramAPIError,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from loguru import logger

T = TypeVar("T")


async def safe_send(
    coro_factory: Callable[[], Coroutine[Any, Any, T]],
    *,
    attempts: int = 3,
) -> T | None:
    """Call coro_factory() up to *attempts* times with smart retry logic.

    - TelegramRetryAfter  -> sleep retry_after seconds, then retry.
    - TelegramNetworkError -> exponential backoff (1, 2, 4 s), then retry.
    - TelegramForbiddenError -> user blocked bot; log warning and return None.
    - Other TelegramAPIError -> log and re-raise immediately.
    - After exhausting attempts -> log and re-raise last exception.
    """
    last_exc: Exception | None = None
    backoff = 1.0

    for attempt in range(1, attempts + 1):
        try:
            return await coro_factory()
        except TelegramForbiddenError as exc:
            logger.warning("Bot blocked by user (TelegramForbiddenError): {}", exc)
            return None
        except TelegramRetryAfter as exc:
            last_exc = exc
            wait = float(exc.retry_after)
            logger.warning(
                "Telegram flood control: retry_after={}s (attempt {}/{})",
                wait,
                attempt,
                attempts,
            )
            if attempt < attempts:
                await asyncio.sleep(wait)
        except TelegramNetworkError as exc:
            last_exc = exc
            logger.warning(
                "Telegram network error: {} (attempt {}/{}), backoff {}s",
                exc,
                attempt,
                attempts,
                backoff,
            )
            if attempt < attempts:
                await asyncio.sleep(backoff)
                backoff *= 2
        except TelegramAPIError as exc:
            logger.error("Unrecoverable TelegramAPIError: {}", exc)
            raise

    logger.error("safe_send exhausted {} attempts, re-raising", attempts)
    raise last_exc  # type: ignore[misc]
