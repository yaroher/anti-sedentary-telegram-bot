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
from ..callbacks import QuestionCb, SnoozeCb, TaskCb
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
    await complete_task(user, task)
    if task.check_question:
        await state.set_state(InputStates.waiting_check_answer)
        await state.update_data(task_id=task.id)
        await query.message.answer(
            t(user.language, "task.check_intro", question=task.check_question),
            reply_markup=question_keyboard(user.language, task.id),
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
    await query.answer()


@router.callback_query(TaskCb.filter(F.action.in_({"skip", "hard"})))
async def cb_task_skip(query: CallbackQuery, callback_data: TaskCb, user: User) -> None:
    assert query.message is not None
    task = await task_repo.find_for_user(callback_data.task_id, user.user_id)
    if not task:
        await query.answer(t(user.language, "task.closed"), show_alert=True)
        return
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
    await query.answer()


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
