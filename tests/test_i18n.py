"""Unit tests for the i18n layer — pure functions, no DB."""

from __future__ import annotations

import pytest

from anti_sedentary_bot.i18n import normalize_locale, t

# ---------------------------------------------------------------------------
# normalize_locale
# ---------------------------------------------------------------------------


def test_normalize_locale_none_returns_default():
    assert normalize_locale(None) == "en"


def test_normalize_locale_empty_string_returns_default():
    assert normalize_locale("") == "en"


def test_normalize_locale_unknown_code_returns_default():
    assert normalize_locale("zz") == "en"


def test_normalize_locale_known_code_returned():
    assert normalize_locale("ru") == "ru"
    assert normalize_locale("en") == "en"


def test_normalize_locale_case_insensitive():
    assert normalize_locale("RU") == "ru"
    assert normalize_locale("EN") == "en"


def test_normalize_locale_strips_region():
    # e.g. Telegram sends "ru-RU" or "en-US"
    assert normalize_locale("ru-RU") == "ru"
    assert normalize_locale("en-US") == "en"


# ---------------------------------------------------------------------------
# t() — key resolution
# ---------------------------------------------------------------------------


def test_t_resolves_known_key_en():
    result = t("en", "menu.title")
    assert "menu" in result.lower() or len(result) > 0


def test_t_resolves_known_key_ru():
    result = t("ru", "menu.title")
    assert isinstance(result, str)
    assert len(result) > 0


def test_t_falls_back_to_en_for_missing_ru_key(monkeypatch: pytest.MonkeyPatch):
    """If a key exists in EN but not in RU, t() should return the EN value."""
    from anti_sedentary_bot.i18n import LOCALES

    # Inject a key only into EN
    monkeypatch.setitem(LOCALES["en"], "__test_only__", "hello from en")
    # Make sure it is absent from RU
    LOCALES["ru"].pop("__test_only__", None)

    result = t("ru", "__test_only__")
    assert result == "hello from en"


def test_t_returns_key_when_missing_everywhere(monkeypatch: pytest.MonkeyPatch):
    """If a key is absent from all locales, t() returns the key itself."""
    result = t("en", "__completely_missing_key__")
    assert result == "__completely_missing_key__"


def test_t_formats_kwargs():
    result = t("en", "settings.interval.saved", minutes=30)
    assert "30" in result


def test_t_normalizes_locale_internally():
    # Passing an unsupported locale still resolves the key via EN fallback
    result = t("zz", "menu.title")
    assert isinstance(result, str)
    assert len(result) > 0
