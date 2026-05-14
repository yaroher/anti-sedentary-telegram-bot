from __future__ import annotations

from pathlib import Path
from typing import Literal

from loguru import logger
from pydantic import BaseModel, Field

ExerciseKind = Literal["strength", "core", "mobility"]


class ExerciseLocale(BaseModel):
    title: str
    instruction: str
    check_questions: list[str] = Field(default_factory=list)


class Exercise(BaseModel):
    code: str
    kind: ExerciseKind
    unlock_seconds: int
    difficulty: int = 1
    locales: dict[str, ExerciseLocale]

    def for_locale(self, locale: str, fallback: str = "en") -> ExerciseLocale:
        return self.locales.get(locale) or self.locales[fallback]


def _default_exercises_path() -> Path:
    return Path(__file__).resolve().parents[3] / "config" / "exercises.yaml"


def _load_exercises() -> list[Exercise]:
    """Load exercises from YAML. Falls back to empty list if file is missing."""

    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("pyyaml not installed; EXERCISES will be empty")
        return []

    # Prefer settings override if settings can be imported without error.
    path: Path | None = None
    try:
        from ..config import settings

        path = settings.resolved_exercises_path
    except Exception:
        pass

    if path is None:
        path = _default_exercises_path()

    if not path.exists():
        logger.warning("exercises.yaml not found at {}; EXERCISES will be empty", path)
        return []

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        exercises = []
        for item in data.get("exercises", []):
            raw_locales = item.pop("locales", {})
            locales = {k: ExerciseLocale(**v) for k, v in raw_locales.items()}
            exercises.append(Exercise(**item, locales=locales))
        return exercises
    except Exception as exc:
        logger.warning("Failed to load exercises.yaml: {}; EXERCISES will be empty", exc)
        return []


EXERCISES: list[Exercise] = _load_exercises()


def find_exercise(code: str) -> Exercise | None:
    return next((e for e in EXERCISES if e.code == code), None)
