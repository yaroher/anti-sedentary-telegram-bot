from __future__ import annotations

from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ...db.models import User
from ...domain.flavors import FLAVORS
from ...i18n import t
from ...services.tasks import active_task, schedule_next_task, send_task
from ...utils.time import in_work_window
from ..keyboards import language_keyboard, main_menu
from ..states import InputStates

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext, user: User, is_new_user: bool) -> None:
    await state.clear()

    if is_new_user:
        await state.set_state(InputStates.onboarding_language)
        await message.answer(
            t(user.language, "start.choose_language"),
            reply_markup=language_keyboard(),
        )
        return

    flavor_title = FLAVORS[user.flavor].for_locale(user.language).title
    welcome = t(
        user.language,
        "start.welcome",
        day_start=user.day_start,
        day_end=user.day_end,
        break_every=user.break_every_minutes,
        flavor=flavor_title,
    )
    await message.answer(welcome, reply_markup=main_menu(user.language))

    if user.is_enabled and in_work_window(user.day_start, user.day_end):
        if not await active_task(user):
            await message.answer(t(user.language, "day.in_window"))
            await send_task(bot, user, reason="start_command")
        await schedule_next_task(user)
