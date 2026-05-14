"""Unit tests for exercise selection and lookup — no DB required."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from anti_sedentary_bot.domain.exercises import Exercise, ExerciseLocale, find_exercise

# ---------------------------------------------------------------------------
# Helpers — build lightweight Exercise objects without touching the YAML
# ---------------------------------------------------------------------------


def _make_exercise(code: str, kind: str = "strength", unlock_seconds: int = 60) -> Exercise:
    return Exercise(
        code=code,
        kind=kind,  # type: ignore[arg-type]
        unlock_seconds=unlock_seconds,
        locales={"en": ExerciseLocale(title=f"Exercise {code}", instruction="Do the thing.")},
    )


# ---------------------------------------------------------------------------
# Stub for DailyState (no DB, no ORM)
# ---------------------------------------------------------------------------


@dataclass
class _FakeDailyState:
    completed_count: int = 0
    pressure_level: int = 0


# ---------------------------------------------------------------------------
# choose_exercise
# ---------------------------------------------------------------------------


def test_choose_exercise_returns_exercise(monkeypatch: pytest.MonkeyPatch):
    """choose_exercise should return an Exercise from the pool."""
    from anti_sedentary_bot.services import exercises as ex_mod

    fake_exercises = [
        _make_exercise("push_up", "strength"),
        _make_exercise("plank", "core"),
        _make_exercise("stretch", "mobility"),
    ]
    monkeypatch.setattr(ex_mod, "EXERCISES", fake_exercises)

    state = _FakeDailyState(completed_count=1, pressure_level=0)
    result = ex_mod.choose_exercise(state)  # type: ignore[arg-type]
    assert isinstance(result, Exercise)
    assert result.code in {"push_up", "plank", "stretch"}


def test_choose_exercise_high_pressure_expands_pool(monkeypatch: pytest.MonkeyPatch):
    """pressure_level >= 2 adds strength/core extras to the pool — they are more likely."""
    from anti_sedentary_bot.services import exercises as ex_mod

    strength = _make_exercise("push_up", "strength")
    mobility = _make_exercise("stretch", "mobility")
    fake_exercises = [strength, mobility]
    monkeypatch.setattr(ex_mod, "EXERCISES", fake_exercises)

    state = _FakeDailyState(completed_count=5, pressure_level=3)

    counts: dict[str, int] = {"push_up": 0, "stretch": 0}
    for _ in range(200):
        r = ex_mod.choose_exercise(state)  # type: ignore[arg-type]
        counts[r.code] += 1

    # strength should appear more often because it's duplicated in the pool
    assert counts["push_up"] > counts["stretch"]


def test_choose_exercise_first_task_prefers_mobility(monkeypatch: pytest.MonkeyPatch):
    """completed_count == 0 adds mobility items to the pool — they are more likely."""
    from anti_sedentary_bot.services import exercises as ex_mod

    strength = _make_exercise("push_up", "strength")
    mobility = _make_exercise("stretch", "mobility")
    fake_exercises = [strength, mobility]
    monkeypatch.setattr(ex_mod, "EXERCISES", fake_exercises)

    state = _FakeDailyState(completed_count=0, pressure_level=0)

    counts: dict[str, int] = {"push_up": 0, "stretch": 0}
    for _ in range(200):
        r = ex_mod.choose_exercise(state)  # type: ignore[arg-type]
        counts[r.code] += 1

    assert counts["stretch"] > counts["push_up"]


# ---------------------------------------------------------------------------
# find_exercise
# ---------------------------------------------------------------------------


def test_find_exercise_found(monkeypatch: pytest.MonkeyPatch):
    from anti_sedentary_bot.domain import exercises as dom

    ex = _make_exercise("push_up")
    monkeypatch.setattr(dom, "EXERCISES", [ex])

    result = find_exercise("push_up")
    assert result is not None
    assert result.code == "push_up"


def test_find_exercise_not_found(monkeypatch: pytest.MonkeyPatch):
    from anti_sedentary_bot.domain import exercises as dom

    monkeypatch.setattr(dom, "EXERCISES", [_make_exercise("push_up")])

    assert find_exercise("nonexistent") is None


def test_find_exercise_empty_list(monkeypatch: pytest.MonkeyPatch):
    from anti_sedentary_bot.domain import exercises as dom

    monkeypatch.setattr(dom, "EXERCISES", [])

    assert find_exercise("anything") is None
