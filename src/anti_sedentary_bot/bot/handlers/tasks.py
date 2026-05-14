from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ...db.models import MessageRole, User
from ...i18n import t
from ...repositories import tasks as task_repo
from ...services.llm import add_message, llm_text
from ...services.tasks import complete_task, skip_task
from ...utils.time import human_time_left, now
from ..callbacks import QuestionCb, RatingCb, SnoozeCb, TaskCb
from ..keyboards import main_menu, question_keyboard, task_keyboard
from ..states import InputStates

router = Router(name="tasks")


@router.callback_query(TaskCb.filter(F.action == "done"))
async def cb_task_done(query: CallbackQuery, callback_data: TaskCb, state: FSMContext, user: User) -> None:
    assert query.message is not None
    task = await task_repo.find_for_user(callback_data.task_id, user.user_id)
    if not task:
        await query.answer(t(user.language, "task.closed"), show_alert=True)
        return
    if now() < task.unlock_at:
        await query.answer(
            t(user.language, "task.early", left=human_time_left(task.unlock_at)),
            show_alert=True,
        )
        return
    # ACK immediately — LLM/retry can take >15s and the callback would expire.
    await query.answer()
    await complete_task(user, task)
    if task.check_question:
        await state.set_state(InputStates.waiting_check_answer)
        await state.update_data(task_id=task.id)
        # Show 1..10 rating buttons when the question asks for a numeric rating.
        q_lower = (task.check_question or "").lower()
        is_rating = any(s in q_lower for s in ("1 до 10", "1 to 10", "1-10", "от 1", "from 1"))
        await query.message.answer(
            t(user.language, "task.check_intro", question=task.check_question),
            reply_markup=question_keyboard(user.language, task.id, rating=is_rating),
        )
    else:
        msg = await llm_text(
            user,
            "praise the user for completion",
            {"task": task.title},
            fallback=t(user.language, "fallback.praise"),
        )
        await add_message(user, MessageRole.ASSISTANT, msg)
        # Edit the original task message so the chat doesn't fill up with menus.
        try:
            await query.message.edit_text(f"✅ {msg}")
        except Exception:
            await query.message.answer(f"✅ {msg}")


@router.callback_query(TaskCb.filter(F.action.in_({"skip", "hard"})))
async def cb_task_skip(query: CallbackQuery, callback_data: TaskCb, user: User) -> None:
    assert query.message is not None
    task = await task_repo.find_for_user(callback_data.task_id, user.user_id)
    if not task:
        await query.answer(t(user.language, "task.closed"), show_alert=True)
        return
    # ACK immediately to avoid callback expiry while LLM runs.
    await query.answer()
    hard = callback_data.action == "hard"
    await skip_task(user, task, hard=hard)
    purpose = "respond to too-hard task" if hard else "respond to skip"
    fb_key = "fallback.hard" if hard else "fallback.skip"
    msg = await llm_text(user, purpose, {"task": task.title, "hard": hard}, fallback=t(user.language, fb_key))
    text = t(user.language, "task.skipped_logged", msg=msg)
    try:
        await query.message.edit_text(text)
    except Exception:
        await query.message.answer(text, reply_markup=main_menu(user.language))


@router.callback_query(SnoozeCb.filter())
async def cb_snooze(query: CallbackQuery, callback_data: SnoozeCb, user: User) -> None:
    assert query.message is not None
    task = await task_repo.find_for_user(callback_data.task_id, user.user_id)
    if not task:
        await query.answer(t(user.language, "task.closed"), show_alert=True)
        return
    result = await task_repo.snooze(task, callback_data.minutes)
    if result is None:
        await query.answer(t(user.language, "task.snooze_exhausted"), show_alert=True)
        return
    await query.message.edit_reply_markup(reply_markup=task_keyboard(user.language, task.id))
    await query.answer(t(user.language, "task.snoozed", n=callback_data.minutes))


@router.callback_query(QuestionCb.filter(F.action == "answer"))
async def cb_question_answer(
    query: CallbackQuery, callback_data: QuestionCb, state: FSMContext, user: User
) -> None:
    assert query.message is not None
    await state.set_state(InputStates.waiting_check_answer)
    await state.update_data(task_id=callback_data.task_id)
    await query.message.answer(t(user.language, "task.check_prompt"))
    await query.answer()


@router.callback_query(QuestionCb.filter(F.action == "skip"))
async def cb_question_skip(query: CallbackQuery, callback_data: QuestionCb, user: User) -> None:
    assert query.message is not None
    await task_repo.skip_check_question(callback_data.task_id, user.user_id)
    await query.message.answer(
        t(user.language, "task.question_skipped"), reply_markup=main_menu(user.language)
    )
    await query.answer()


@router.callback_query(RatingCb.filter())
async def cb_rating(query: CallbackQuery, callback_data: RatingCb, state: FSMContext, user: User) -> None:
    """Inline rating button (1..10) used as quick check-answer."""
    from ...repositories import tasks as t_repo
    from ...services import calibration

    assert query.message is not None
    task = await t_repo.find_any_for_user(callback_data.task_id, user.user_id)
    if task is None:
        await query.answer(t(user.language, "task.closed"), show_alert=True)
        return

    rating = int(callback_data.value)
    await t_repo.set_difficulty_rating(callback_data.task_id, user.user_id, rating)
    task.difficulty_rating = rating
    task.check_answer = str(rating)
    await task.save(update_fields=["difficulty_rating", "check_answer"])
    await calibration.apply_difficulty_rating(user, task)
    await state.clear()

    try:
        await query.message.edit_text(
            t(user.language, "task.check_intro", question=task.check_question) + f"\n\n<b>{rating}/10</b> ✅"
        )
    except Exception:
        await query.message.answer(f"{rating}/10 ✅", reply_markup=main_menu(user.language))
    await query.answer()
