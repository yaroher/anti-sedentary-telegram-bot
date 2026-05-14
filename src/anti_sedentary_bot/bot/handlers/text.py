from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ...db.models import MessageRole, User
from ...i18n import t
from ...repositories import tasks as task_repo
from ...repositories import users as user_repo
from ...services.llm import add_message, llm_text
from ...services.tasks import schedule_next_task
from ...utils.time import parse_hhmm
from ..keyboards import main_menu
from ..states import InputStates

router = Router(name="text")


@router.message(InputStates.waiting_schedule, F.text)
async def on_schedule_input(message: Message, state: FSMContext, user: User) -> None:
    text = (message.text or "").strip()
    try:
        normalized = text.replace("—", "-").replace("–", "-").replace(" ", "")
        start, end = normalized.split("-")
        parse_hhmm(start)
        parse_hhmm(end)
    except Exception:
        await message.answer(t(user.language, "settings.schedule.bad_format"))
        return
    await user_repo.set_schedule(user, start, end)
    await schedule_next_task(user)
    await state.clear()
    await message.answer(
        t(user.language, "settings.schedule.saved", day_start=start, day_end=end),
        reply_markup=main_menu(user.language),
    )


@router.message(InputStates.waiting_check_answer, F.text)
async def on_check_answer(message: Message, state: FSMContext, user: User) -> None:
    text = (message.text or "").strip()
    data = await state.get_data()
    task_id = data.get("task_id")
    if not task_id:
        await state.clear()
        await message.answer(t(user.language, "text.context_lost"), reply_markup=main_menu(user.language))
        return

    suspicious = len(text) < 2 or text.lower() in {"норм", "ок", "да", "+", "ok", "yes", "fine"}
    await add_message(user, MessageRole.USER, text)
    task = await task_repo.find_any_for_user(task_id, user.user_id)
    if task:
        task.check_answer = text[:1000]
        if suspicious:
            task.suspicious = True
        await task.save(update_fields=["check_answer", "suspicious"])

    await state.clear()
    reaction = await llm_text(
        user,
        "respond to check answer",
        {"answer": text, "suspicious": suspicious},
    )
    await add_message(user, MessageRole.ASSISTANT, reaction)
    await message.answer(reaction, reply_markup=main_menu(user.language))


@router.message(F.text)
async def on_text_fallback(message: Message, user: User) -> None:
    await message.answer(t(user.language, "text.fallback"), reply_markup=main_menu(user.language))
