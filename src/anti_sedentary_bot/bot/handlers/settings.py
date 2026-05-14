from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ...db.models import User
from ...domain.flavors import FLAVORS
from ...i18n import language_label, normalize_locale, t
from ...repositories import users as user_repo
from ...services.tasks import schedule_next_task
from .._ui import edit_or_send
from ..callbacks import FlavorCb, IntervalCb, LanguageCb, MenuCb, QuietCb, ScheduleCb
from ..keyboards import (
    flavor_keyboard,
    interval_keyboard,
    language_keyboard,
    main_menu,
    quiet_keyboard,
    schedule_keyboard,
)
from ..states import InputStates

router = Router(name="settings")


@router.callback_query(MenuCb.filter(F.action == "settings_schedule"))
async def cb_schedule(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await edit_or_send(
        query.message,
        t(user.language, "settings.schedule.current", day_start=user.day_start, day_end=user.day_end),
        reply_markup=schedule_keyboard(user.language),
    )
    await query.answer()


@router.callback_query(ScheduleCb.filter())
async def cb_schedule_set(query: CallbackQuery, callback_data: ScheduleCb, user: User) -> None:
    assert query.message is not None
    start = callback_data.start.replace("-", ":")
    end = callback_data.end.replace("-", ":")
    await user_repo.set_schedule(user, start, end)
    await schedule_next_task(user)
    await edit_or_send(
        query.message,
        t(user.language, "settings.schedule.saved", day_start=start, day_end=end),
        reply_markup=main_menu(user.language),
    )
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "schedule_custom"))
async def cb_schedule_custom(query: CallbackQuery, state: FSMContext, user: User) -> None:
    assert query.message is not None
    await state.set_state(InputStates.waiting_schedule)
    await edit_or_send(query.message, t(user.language, "settings.schedule.custom_prompt"))
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "settings_flavor"))
async def cb_flavor(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await edit_or_send(
        query.message, t(user.language, "settings.flavor.prompt"), reply_markup=flavor_keyboard(user.language)
    )
    await query.answer()


@router.callback_query(FlavorCb.filter())
async def cb_flavor_set(query: CallbackQuery, callback_data: FlavorCb, user: User) -> None:
    assert query.message is not None
    if callback_data.key not in FLAVORS:
        await query.answer(t(user.language, "settings.flavor.unknown"), show_alert=True)
        return
    await user_repo.set_flavor(user, callback_data.key)
    title = FLAVORS[callback_data.key].for_locale(user.language).title
    await edit_or_send(
        query.message,
        t(user.language, "settings.flavor.saved", title=title),
        reply_markup=main_menu(user.language),
    )
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "settings_interval"))
async def cb_interval(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await edit_or_send(
        query.message,
        t(user.language, "settings.interval.prompt"),
        reply_markup=interval_keyboard(user.language),
    )
    await query.answer()


@router.callback_query(IntervalCb.filter())
async def cb_interval_set(query: CallbackQuery, callback_data: IntervalCb, user: User) -> None:
    assert query.message is not None
    await user_repo.set_interval(user, callback_data.minutes)
    await schedule_next_task(user)
    await edit_or_send(
        query.message,
        t(user.language, "settings.interval.saved", minutes=callback_data.minutes),
        reply_markup=main_menu(user.language),
    )
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "settings_toggle"))
async def cb_toggle(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await user_repo.set_enabled(user, not user.is_enabled)
    key = "settings.toggle.enabled" if user.is_enabled else "settings.toggle.paused"
    await edit_or_send(query.message, t(user.language, key), reply_markup=main_menu(user.language))
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "settings_language"))
async def cb_language(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await edit_or_send(
        query.message, t(user.language, "settings.language.prompt"), reply_markup=language_keyboard()
    )
    await query.answer()


@router.callback_query(MenuCb.filter(F.action == "settings_quiet"))
async def cb_quiet(query: CallbackQuery, user: User) -> None:
    assert query.message is not None
    await edit_or_send(
        query.message, t(user.language, "settings.quiet.prompt"), reply_markup=quiet_keyboard(user.language)
    )
    await query.answer()


@router.callback_query(QuietCb.filter())
async def cb_quiet_set(query: CallbackQuery, callback_data: QuietCb, user: User) -> None:
    assert query.message is not None
    if callback_data.value == "off":
        await user_repo.set_quiet_hours(user, None, None)
        await edit_or_send(
            query.message, t(user.language, "settings.quiet.off"), reply_markup=main_menu(user.language)
        )
    else:
        parts = callback_data.value.split("_")
        start = parts[0].replace("-", ":")
        end = parts[1].replace("-", ":")
        await user_repo.set_quiet_hours(user, start, end)
        await edit_or_send(
            query.message,
            t(user.language, "settings.quiet.saved", start=start, end=end),
            reply_markup=main_menu(user.language),
        )
    await query.answer()


@router.callback_query(LanguageCb.filter())
async def cb_language_set(
    query: CallbackQuery, callback_data: LanguageCb, state: FSMContext, user: User
) -> None:
    assert query.message is not None
    code = normalize_locale(callback_data.code)
    await user_repo.set_language(user, code)
    current = await state.get_state()
    if current == InputStates.onboarding_language.state:
        await state.clear()
    await edit_or_send(
        query.message,
        t(code, "start.language_set", lang=language_label(code)),
        reply_markup=main_menu(code),
    )
    await query.answer()
