from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..domain.flavors import FLAVORS
from ..i18n import SUPPORTED, language_label, t
from .callbacks import (
    FlavorCb,
    IntervalCb,
    LanguageCb,
    MenuCb,
    QuestionCb,
    QuietCb,
    ScheduleCb,
    SnoozeCb,
    TaskCb,
)


def main_menu(locale: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(locale, "menu.day_start"), callback_data=MenuCb(action="day_start"))
    b.button(text=t(locale, "menu.stats"), callback_data=MenuCb(action="stats"))
    b.button(text=t(locale, "menu.schedule"), callback_data=MenuCb(action="settings_schedule"))
    b.button(text=t(locale, "menu.flavor"), callback_data=MenuCb(action="settings_flavor"))
    b.button(text=t(locale, "menu.interval"), callback_data=MenuCb(action="settings_interval"))
    b.button(text=t(locale, "menu.toggle"), callback_data=MenuCb(action="settings_toggle"))
    b.button(text=t(locale, "menu.language"), callback_data=MenuCb(action="settings_language"))
    b.button(text=t(locale, "menu.quiet"), callback_data=MenuCb(action="settings_quiet"))
    b.adjust(1)
    return b.as_markup()


def task_keyboard(locale: str, task_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(locale, "task.btn_done"), callback_data=TaskCb(action="done", task_id=task_id))
    b.button(text=t(locale, "task.btn_hard"), callback_data=TaskCb(action="hard", task_id=task_id))
    b.button(text=t(locale, "task.btn_skip"), callback_data=TaskCb(action="skip", task_id=task_id))
    b.button(text=t(locale, "task.btn_snooze", n=5), callback_data=SnoozeCb(task_id=task_id, minutes=5))
    b.button(text=t(locale, "menu.stats"), callback_data=MenuCb(action="stats"))
    b.adjust(1)
    return b.as_markup()


def quiet_keyboard(locale: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    presets = [("13:00", "14:00"), ("12:00", "13:00"), ("18:00", "19:00")]
    for start, end in presets:
        b.button(
            text=f"{start}–{end}",
            callback_data=QuietCb(value=f"{start.replace(':', '-')}_{end.replace(':', '-')}"),
        )
    b.button(text=t(locale, "settings.quiet.off"), callback_data=QuietCb(value="off"))
    b.button(text=t(locale, "menu.back"), callback_data=MenuCb(action="menu"))
    b.adjust(1)
    return b.as_markup()


def question_keyboard(locale: str, task_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(
        text=t(locale, "task.question_answer"),
        callback_data=QuestionCb(action="answer", task_id=task_id),
    )
    b.button(
        text=t(locale, "task.question_skip"),
        callback_data=QuestionCb(action="skip", task_id=task_id),
    )
    b.adjust(1)
    return b.as_markup()


def flavor_keyboard(locale: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, flavor in FLAVORS.items():
        b.button(text=flavor.for_locale(locale).title, callback_data=FlavorCb(key=key))
    b.button(text=t(locale, "menu.back"), callback_data=MenuCb(action="menu"))
    b.adjust(1)
    return b.as_markup()


def interval_keyboard(locale: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for minutes in (30, 45, 60, 90):
        b.button(
            text=t(locale, "settings.interval.minutes", n=minutes),
            callback_data=IntervalCb(minutes=minutes),
        )
    b.button(text=t(locale, "menu.back"), callback_data=MenuCb(action="menu"))
    b.adjust(2, 2, 1)
    return b.as_markup()


def schedule_keyboard(locale: str) -> InlineKeyboardMarkup:
    presets = [("11:00", "18:00"), ("10:00", "18:00"), ("09:00", "17:00")]
    b = InlineKeyboardBuilder()
    for start, end in presets:
        b.button(
            text=f"{start}–{end}",
            callback_data=ScheduleCb(start=start.replace(":", "-"), end=end.replace(":", "-")),
        )
    b.button(
        text=t(locale, "settings.schedule.custom_button"), callback_data=MenuCb(action="schedule_custom")
    )
    b.button(text=t(locale, "menu.back"), callback_data=MenuCb(action="menu"))
    b.adjust(1)
    return b.as_markup()


def language_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for code in SUPPORTED:
        b.button(text=language_label(code), callback_data=LanguageCb(code=code))
    b.adjust(1)
    return b.as_markup()
