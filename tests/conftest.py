"""pytest configuration and shared fixtures."""

from __future__ import annotations

import os

# Set required env vars BEFORE any project imports so pydantic-settings picks them up.
os.environ.setdefault("BOT_TOKEN", "1234567890:AAFakeTokenForTestingPurposesOnly")
os.environ.setdefault("DATABASE_URL", "sqlite://:memory:")

import asyncio
from collections.abc import AsyncGenerator

import pytest
from tortoise import Tortoise

# ---------------------------------------------------------------------------
# Event loop — session-scoped so DB fixtures can be session-scoped too.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def event_loop():
    """Provide a session-scoped event loop for pytest-asyncio."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Tortoise ORM init / teardown
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
async def tortoise_db():
    """Initialise Tortoise with an in-memory SQLite DB and generate schemas."""
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["anti_sedentary_bot.db.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


# ---------------------------------------------------------------------------
# Per-test DB cleanup so tests remain isolated.
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
async def _clean_db(tortoise_db: None) -> AsyncGenerator[None, None]:
    """Truncate all tables before each test."""
    yield
    from anti_sedentary_bot.db.models import ChatMessage, DailyState, Task, User

    await ChatMessage.all().delete()
    await Task.all().delete()
    await DailyState.all().delete()
    await User.all().delete()
