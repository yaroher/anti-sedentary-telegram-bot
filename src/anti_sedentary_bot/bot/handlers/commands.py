from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ...db.models import User
from ...i18n import t
from ...repositories import users as user_repo
from ...services.tasks import active_task
from ...services.user import get_daily_state
from ...utils.time import human_time_left
from ..keyboards import language_keyboard, main_menu, quiet_keyboard

router = Router(name="commands")


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
