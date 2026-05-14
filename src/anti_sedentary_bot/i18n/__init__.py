from __future__ import annotations

from typing import Any

from .locales.en import STRINGS as EN
from .locales.ru import STRINGS as RU

LOCALES: dict[str, dict[str, str]] = {"en": EN, "ru": RU}
SUPPORTED: tuple[str, ...] = tuple(LOCALES.keys())
DEFAULT_LOCALE = "en"


def normalize_locale(code: str | None) -> str:
    if not code:
        return DEFAULT_LOCALE
    code = code.lower().split("-")[0]
    return code if code in LOCALES else DEFAULT_LOCALE


def t(locale: str, key: str, /, **kwargs: Any) -> str:
    locale = normalize_locale(locale)
    template = LOCALES[locale].get(key) or LOCALES[DEFAULT_LOCALE].get(key) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template


def language_label(code: str) -> str:
    return {"en": "English", "ru": "Русский"}.get(code, code)
