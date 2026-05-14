from __future__ import annotations

from datetime import datetime

from ..db.models import ChatMessage, MessageRole, User


async def add(user: User, role: MessageRole, content: str) -> None:
    await ChatMessage.create(user=user, role=role, content=content[:4000])


async def recent(user: User, limit: int) -> list[ChatMessage]:
    msgs = await ChatMessage.filter(user=user).order_by("-id").limit(limit)
    return list(reversed(msgs))


async def delete_older_than(cutoff: datetime) -> int:
    """Delete all ChatMessage rows created before *cutoff*. Returns deleted row count."""
    deleted_count, _ = await ChatMessage.filter(created_at__lt=cutoff).delete()
    return deleted_count
