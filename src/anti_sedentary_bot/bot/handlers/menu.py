from __future__ import annotations

from datetime import timedelta

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ...db.models import User
from ...i18n import t
from ...services.tasks import active_task, schedule_next_task, send_task
from ...services.user import get_daily_state
from ...utils.time import human_time_left, in_work_window, now, work_window_bounds
from .._ui import edit_or_send
from ..callbacks import MenuCb
from ..keyboards import main_menu

router = Router(name="menu")


@router.callback_query(MenuCb.filter(F.action == "menu"))
async def cb_menu(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await query.message.edit_text(t(user.language, "menu.title"), reply_markup=main_menu(user.language))
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "day_start"))
async def cb_day_start(query: CallbackQuery, bot: Bot, user: User) -> None:
    assert query.message is not None
    if not user.is_enabled:
        user.is_enabled = True
        await user.save(update_fields=["is_enabled", "updated_at"])

    if in_work_window(user.day_start, user.day_end):
        await query.answer(t(user.language, "day.work_mode_on"))
        await edit_or_send(query.message, t(user.language, "day.in_window"))
        await send_task(bot, user, reason="manual_start")
    else:
        await schedule_next_task(user)
        start_dt, _ = work_window_bounds(user.day_start, user.day_end)
        if start_dt < now():
            start_dt += timedelta(days=1)
        await edit_or_send(
            query.message,
            t(user.language, "day.out_of_window", when=start_dt.strftime("%H:%M")),
            reply_markup=main_menu(user.language),
        )
        await query.answer()


@router.callback_query(MenuCb.filter(F.action == "stats"))
async def cb_stats(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    state = await get_daily_state(user)
    task = await active_task(user)
    if task:
        active_line = t(
            user.language,
            "stats.active",
            title=task.title,
            left=human_time_left(task.unlock_at),
        )
    else:
        active_line = t(user.language, "stats.no_active")
    body = t(
        user.language,
        "stats.body",
        completed=state.completed_count,
        skipped=state.skipped_count,
        failed=state.failed_count,
        streak=state.streak,
        pressure=state.pressure_level,
        active_line=active_line,
    )
    await edit_or_send(query.message, body, reply_markup=main_menu(user.language))
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "talk_end"))
async def cb_talk_end(query: CallbackQuery, user: User, state: FSMContext) -> None:
    assert query.message is not None
    await state.clear()
    await edit_or_send(query.message, t(user.language, "talk.ended"), reply_markup=main_menu(user.language))
    await query.answer()
