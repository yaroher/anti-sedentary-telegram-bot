from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from ...db.models import User
from ...i18n import t
from ...repositories import habit_events as he_repo
from ...repositories import users as user_repo
from ..callbacks import HealthCb, MenuCb
from ..keyboards import health_keyboard

router = Router(name="health")


# ---------------------------------------------------------------------------
# Settings sub-menu
# ---------------------------------------------------------------------------


@router.callback_query(MenuCb.filter(F.action == "settings_health"))
async def cb_settings_health(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await query.message.answer(
        t(user.language, "settings.health.prompt"),
        reply_markup=health_keyboard(user, user.language),
    )
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "toggle_eye"))
async def cb_toggle_eye(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await user_repo.set_health_track(user, "eye", not user.eye_break_enabled)
    await query.message.edit_reply_markup(reply_markup=health_keyboard(user, user.language))
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "toggle_hydration"))
async def cb_toggle_hydration(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await user_repo.set_health_track(user, "hydration", not user.hydration_enabled)
    await query.message.edit_reply_markup(reply_markup=health_keyboard(user, user.language))
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "toggle_posture"))
async def cb_toggle_posture(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await user_repo.set_health_track(user, "posture", not user.posture_enabled)
    await query.message.edit_reply_markup(reply_markup=health_keyboard(user, user.language))
    await query.answer()


# ---------------------------------------------------------------------------
# Done acknowledgement
# ---------------------------------------------------------------------------


@router.callback_query(HealthCb.filter())
async def cb_health_done(query: CallbackQuery, callback_data: HealthCb, user: User) -> None:
    assert query.message is not None
    kind = callback_data.kind
    await he_repo.record(user, kind)
    ack = t(user.language, f"health.{kind}.ack")
    await query.message.edit_text(ack)
    await query.answer(ack)
