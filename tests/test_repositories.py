"""Tests for the users repository — get_or_create, soft_delete, restore, list_enabled."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from anti_sedentary_bot.db.models import User
from anti_sedentary_bot.repositories import users as user_repo

# ---------------------------------------------------------------------------
# Helper — build a minimal fake TgUser
# ---------------------------------------------------------------------------


def _tg_user(user_id: int, username: str = "testuser", language_code: str = "en"):
    """Return a mock that quacks like aiogram.types.User."""
    mock = MagicMock()
    mock.id = user_id
    mock.username = username
    mock.first_name = "Test"
    mock.language_code = language_code
    return mock


# ---------------------------------------------------------------------------
# get_or_create_from_tg
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_or_create_first_call_returns_created(tortoise_db: None):
    tg_user = _tg_user(5001)
    user, created = await user_repo.get_or_create_from_tg(tg_user)

    assert created is True
    assert user.user_id == 5001
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_or_create_second_call_returns_not_created(tortoise_db: None):
    tg_user = _tg_user(5002)
    user1, created1 = await user_repo.get_or_create_from_tg(tg_user)
    user2, created2 = await user_repo.get_or_create_from_tg(tg_user)

    assert created1 is True
    assert created2 is False
    assert user1.user_id == user2.user_id


@pytest.mark.asyncio
async def test_get_or_create_same_user_id_same_row(tortoise_db: None):
    tg_user = _tg_user(5003)
    _, _ = await user_repo.get_or_create_from_tg(tg_user)
    _, _ = await user_repo.get_or_create_from_tg(tg_user)

    count = await User.filter(user_id=5003).count()
    assert count == 1


# ---------------------------------------------------------------------------
# soft_delete and restore
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_soft_delete_marks_is_deleted(tortoise_db: None):
    tg_user = _tg_user(6001)
    user, _ = await user_repo.get_or_create_from_tg(tg_user)

    await user_repo.soft_delete(user)

    refreshed = await User.get(user_id=6001)
    assert refreshed.is_deleted is True
    assert refreshed.deleted_at is not None


@pytest.mark.asyncio
async def test_restore_clears_is_deleted(tortoise_db: None):
    tg_user = _tg_user(6002)
    user, _ = await user_repo.get_or_create_from_tg(tg_user)
    await user_repo.soft_delete(user)

    await user_repo.restore(user)

    refreshed = await User.get(user_id=6002)
    assert refreshed.is_deleted is False
    assert refreshed.deleted_at is None


# ---------------------------------------------------------------------------
# list_enabled
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_enabled_excludes_deleted(tortoise_db: None):
    active_tg = _tg_user(7001, "active")
    deleted_tg = _tg_user(7002, "deleted")

    active_user, _ = await user_repo.get_or_create_from_tg(active_tg)
    deleted_user, _ = await user_repo.get_or_create_from_tg(deleted_tg)
    await user_repo.soft_delete(deleted_user)

    enabled = await user_repo.list_enabled()
    ids = {u.user_id for u in enabled}

    assert 7001 in ids
    assert 7002 not in ids


@pytest.mark.asyncio
async def test_list_enabled_excludes_paused(tortoise_db: None):
    active_tg = _tg_user(7003, "always_on")
    paused_tg = _tg_user(7004, "paused")

    active_user, _ = await user_repo.get_or_create_from_tg(active_tg)
    paused_user, _ = await user_repo.get_or_create_from_tg(paused_tg)

    paused_user.is_enabled = False
    await paused_user.save(update_fields=["is_enabled", "updated_at"])

    enabled = await user_repo.list_enabled()
    ids = {u.user_id for u in enabled}

    assert 7003 in ids
    assert 7004 not in ids


@pytest.mark.asyncio
async def test_list_enabled_restored_user_reappears(tortoise_db: None):
    tg_user = _tg_user(7005, "comes_back")
    user, _ = await user_repo.get_or_create_from_tg(tg_user)

    await user_repo.soft_delete(user)
    before = {u.user_id for u in await user_repo.list_enabled()}
    assert 7005 not in before

    await user_repo.restore(user)
    after = {u.user_id for u in await user_repo.list_enabled()}
    assert 7005 in after
