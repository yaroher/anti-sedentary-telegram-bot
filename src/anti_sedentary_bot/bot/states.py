from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class InputStates(StatesGroup):
    onboarding_language = State()
    waiting_schedule = State()
    waiting_check_answer = State()
    talking_to_coach = State()
