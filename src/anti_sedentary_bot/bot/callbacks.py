from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class MenuCb(CallbackData, prefix="menu"):
    action: str  # menu | day_start | stats | settings_schedule | settings_flavor | settings_interval | settings_toggle | settings_language | schedule_custom


class TaskCb(CallbackData, prefix="task"):
    action: str  # done | skip | hard
    task_id: int


class QuestionCb(CallbackData, prefix="question"):
    action: str  # answer | skip
    task_id: int


class FlavorCb(CallbackData, prefix="flavor"):
    key: str


class IntervalCb(CallbackData, prefix="interval"):
    minutes: int


class ScheduleCb(CallbackData, prefix="schedule"):
    start: str  # HH-MM
    end: str  # HH-MM


class LanguageCb(CallbackData, prefix="lang"):
    code: str


class SnoozeCb(CallbackData, prefix="snooze"):
    task_id: int
    minutes: int


class QuietCb(CallbackData, prefix="quiet"):
    # start/end are "HH-MM" or "off"
    value: str
