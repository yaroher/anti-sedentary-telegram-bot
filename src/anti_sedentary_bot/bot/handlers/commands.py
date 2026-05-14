from __future__ import annotations

import contextlib
from datetime import timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ...db.models import User
from ...i18n import t
from ...repositories import busy_periods as busy_repo
from ...repositories import tasks as task_repo
from ...repositories import users as user_repo
from ...services.tasks import active_task, skip_task
from ...services.user import get_daily_state
from ...utils.time import human_time_left, now
from ..keyboards import language_keyboard, main_menu, quiet_keyboard

router = Router(name="commands")

MAX_BUSY_MINUTES = 240


@router.message(Command("menu"))
async def cmd_menu(message: Message, user: User) -> None:
    await message.answer(t(user.language, "menu.title"), reply_markup=main_menu(user.language))


@router.message(Command("stats"))
async def cmd_stats(message: Message, user: User) -> None:
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
    # Append baseline progress if in baseline
    from ...services.calibration import is_in_baseline

    if is_in_baseline(user):
        total_completed = await task_repo.count_all_completed(user)
        baseline_note = t(user.language, "baseline.progress", completed=total_completed)
        body = f"{body}\n\n{baseline_note}"

    await message.answer(body, reply_markup=main_menu(user.language))


@router.message(Command("pause"))
async def cmd_pause(message: Message, user: User) -> None:
    await user_repo.set_enabled(user, False)
    await message.answer(t(user.language, "settings.toggle.paused"), reply_markup=main_menu(user.language))


@router.message(Command("resume"))
async def cmd_resume(message: Message, user: User) -> None:
    await user_repo.set_enabled(user, True)
    await message.answer(t(user.language, "settings.toggle.enabled"), reply_markup=main_menu(user.language))


@router.message(Command("lang"))
async def cmd_lang(message: Message, user: User) -> None:
    await message.answer(t(user.language, "settings.language.prompt"), reply_markup=language_keyboard())


@router.message(Command("quiet"))
async def cmd_quiet(message: Message, user: User) -> None:
    await message.answer(
        t(user.language, "settings.quiet.prompt"), reply_markup=quiet_keyboard(user.language)
    )


@router.message(Command("did"))
async def cmd_did(message: Message, user: User) -> None:
    """Mark the user as having done something for N minutes (default 30).

    Closes any unlocked active task as completed (no suspicious flag).
    If task is still locked, soft-skips it without raising pressure.
    """
    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)
    minutes = 30
    if len(parts) > 1:
        with contextlib.suppress(ValueError):
            minutes = max(1, int(parts[1]))

    ends_at = now() + timedelta(minutes=minutes)
    await busy_repo.create(user, reason="did", ends_at=ends_at)

    # Handle active task
    task = await active_task(user)
    if task is not None:
        if now() >= task.unlock_at:
            # Task is unlocked — mark completed without suspicion

            await task_repo.mark_completed(task)
            from ...repositories import daily_states as ds_repo
            from ...services.user import ensure_daily_state

            state = await ensure_daily_state(user)
            await ds_repo.bump_completed(state)
            from ...services.tasks import schedule_next_task

            await schedule_next_task(user)
        else:
            # Still locked — soft skip (hard=True means no pressure increase)
            await skip_task(user, task, hard=True)

    await message.answer(
        t(user.language, "silence.did_logged", minutes=minutes),
        reply_markup=main_menu(user.language),
    )


@router.message(Command("busy"))
async def cmd_busy(message: Message, user: User) -> None:
    """Set busy period for N minutes. Pauses all scheduler activity."""
    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            t(user.language, "silence.busy_usage"),
            reply_markup=main_menu(user.language),
        )
        return

    try:
        minutes = int(parts[1])
    except ValueError:
        await message.answer(
            t(user.language, "silence.busy_usage"),
            reply_markup=main_menu(user.language),
        )
        return

    capped = False
    if minutes > MAX_BUSY_MINUTES:
        minutes = MAX_BUSY_MINUTES
        capped = True

    ends_at = now() + timedelta(minutes=minutes)
    await busy_repo.create(user, reason="busy", ends_at=ends_at)

    reply = t(user.language, "silence.busy_set", minutes=minutes)
    if capped:
        reply += "\n" + t(user.language, "silence.busy_capped", max=MAX_BUSY_MINUTES)

    await message.answer(reply, reply_markup=main_menu(user.language))


@router.message(Command("goal"))
async def cmd_goal(message: Message, user: User) -> None:
    """Set daily task goal. Usage: /goal <N> where 1 <= N <= 20."""
    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            t(user.language, "settings.goal.invalid"),
            reply_markup=main_menu(user.language),
        )
        return

    try:
        n = int(parts[1])
    except ValueError:
        await message.answer(
            t(user.language, "settings.goal.invalid"),
            reply_markup=main_menu(user.language),
        )
        return

    if n < 1 or n > 20:
        await message.answer(
            t(user.language, "settings.goal.invalid"),
            reply_markup=main_menu(user.language),
        )
        return

    await user_repo.set_daily_goal(user, n)
    await message.answer(
        t(user.language, "settings.goal.saved", n=n),
        reply_markup=main_menu(user.language),
    )


@router.message(Command("insights"))
async def cmd_insights(message: Message, user: User) -> None:
    from ...services.insights import build_insights

    text = await build_insights(user)
    await message.answer(text, reply_markup=main_menu(user.language))


@router.message(Command("talk"))
async def cmd_talk(message: Message, user: User, state: FSMContext) -> None:
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    from ..callbacks import MenuCb
    from ..states import InputStates

    await state.set_state(InputStates.talking_to_coach)
    await state.update_data(turns=0)
    b = InlineKeyboardBuilder()
    b.button(text=t(user.language, "talk.end_btn"), callback_data=MenuCb(action="talk_end"))
    b.adjust(1)
    await message.answer(t(user.language, "talk.intro"), reply_markup=b.as_markup())
