from __future__ import annotations

import re

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

# Regex to find a number 1-10 in text (e.g. "7", "7/10", "10")
_RATING_RE = re.compile(r"\b(10|[1-9])\b")


def _extract_rating(text: str) -> int | None:
    """Extract first number 1-10 from text, or None."""
    m = _RATING_RE.search(text)
    if m:
        return int(m.group(1))
    return None


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

        # Parse difficulty rating from answer
        rating = _extract_rating(text)
        if rating is not None:
            await task_repo.set_difficulty_rating(task_id, user.user_id, rating)
            task.difficulty_rating = rating
            # Apply offset adjustments
            from ...services import calibration

            await calibration.apply_difficulty_rating(user, task)

    await state.clear()
    reaction = await llm_text(
        user,
        "respond to check answer",
        {"answer": text, "suspicious": suspicious},
        fallback=t(user.language, "fallback.check_reaction"),
    )
    await add_message(user, MessageRole.ASSISTANT, reaction)
    await message.answer(reaction, reply_markup=main_menu(user.language))


_MAX_COACH_TURNS = 20


@router.message(InputStates.talking_to_coach, F.text)
async def on_coach_message(message: Message, state: FSMContext, user: User) -> None:
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    from ...repositories import messages as msg_repo
    from ..callbacks import MenuCb

    text = (message.text or "").strip()
    data = await state.get_data()
    turns = int(data.get("turns", 0))

    if turns >= _MAX_COACH_TURNS:
        await state.clear()
        await message.answer(t(user.language, "talk.timeout"), reply_markup=main_menu(user.language))
        return

    await msg_repo.add(user, MessageRole.USER, text)
    reply = await llm_text(
        user,
        "coach mode chat with the user, short reply",
        {"user_message": text},
        fallback=t(user.language, "fallback.coach"),
    )
    await msg_repo.add(user, MessageRole.ASSISTANT, reply)

    await state.update_data(turns=turns + 1)
    b = InlineKeyboardBuilder()
    b.button(text=t(user.language, "talk.end_btn"), callback_data=MenuCb(action="talk_end"))
    b.adjust(1)
    await message.answer(reply, reply_markup=b.as_markup())


@router.message(F.text)
async def on_text_fallback(message: Message, user: User) -> None:
    await message.answer(t(user.language, "text.fallback"), reply_markup=main_menu(user.language))
