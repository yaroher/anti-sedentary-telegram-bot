from __future__ import annotations

from datetime import UTC, datetime, timedelta

from loguru import logger

from ..config import settings
from ..repositories import messages as messages_repo


async def run_message_cleanup() -> int:
    """Delete ChatMessage rows older than *message_retention_days*. Returns deleted count."""
    cutoff = datetime.now(tz=UTC) - timedelta(days=settings.message_retention_days)
    deleted = await messages_repo.delete_older_than(cutoff)
    logger.info(
        "Message cleanup: deleted {} rows older than {} days (cutoff={})",
        deleted,
        settings.message_retention_days,
        cutoff.isoformat(),
    )
    return deleted
