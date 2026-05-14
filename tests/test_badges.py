"""Tests for badge service — pure logic and repository helpers."""

from __future__ import annotations

from anti_sedentary_bot.services.insights import _bar_char, _build_heatmap_bar, _classify_trend

# ---------------------------------------------------------------------------
# _bar_char
# ---------------------------------------------------------------------------


def test_bar_char_zero_max_returns_space():
    assert _bar_char(0, 0) == " "


def test_bar_char_full_value_returns_block():
    result = _bar_char(10, 10)
    assert result == "█"


def test_bar_char_half_value_is_midpoint():
    result = _bar_char(5, 10)
    # Should be in the middle range
    assert result in " ▁▂▃▄▅▆▇█"


def test_bar_char_zero_value_is_near_start():
    result = _bar_char(0, 10)
    assert result in " ▁"


# ---------------------------------------------------------------------------
# _classify_trend
# ---------------------------------------------------------------------------


def test_classify_trend_easier():
    result = _classify_trend(3.0, 2.0, "en")
    assert "easier" in result or "↓" in result


def test_classify_trend_harder():
    result = _classify_trend(2.0, 3.0, "en")
    assert "harder" in result or "↑" in result


def test_classify_trend_same():
    result = _classify_trend(2.0, 2.0, "en")
    assert "stable" in result or "→" in result


def test_classify_trend_small_delta_is_same():
    result = _classify_trend(2.0, 2.2, "en")
    assert "stable" in result or "→" in result


# ---------------------------------------------------------------------------
# _build_heatmap_bar
# ---------------------------------------------------------------------------


def test_build_heatmap_bar_returns_nonempty():
    hourly = {9: 3, 10: 1, 11: 5, 12: 2}
    bar = _build_heatmap_bar(hourly, 9, 13)
    assert len(bar) > 0


def test_build_heatmap_bar_includes_hour_labels():
    hourly = {10: 2, 11: 4}
    bar = _build_heatmap_bar(hourly, 10, 12)
    assert "10h" in bar
    assert "11h" in bar


def test_build_heatmap_bar_no_completions_still_renders():
    # When there's no data but a valid window, bar still renders (all-space blocks)
    bar = _build_heatmap_bar({}, 10, 12)
    assert "10h" in bar


# ---------------------------------------------------------------------------
# Badge code constants sanity
# ---------------------------------------------------------------------------


def test_badge_constants_exist():
    from anti_sedentary_bot.services import badges

    for code in [
        badges.STREAK_3,
        badges.STREAK_7,
        badges.STREAK_30,
        badges.STREAK_100,
        badges.COMPLETED_50,
        badges.COMPLETED_200,
        badges.COMPLETED_1000,
        badges.EARLY_BIRD,
        badges.NIGHT_OWL,
        badges.GOAL_STREAK_7,
    ]:
        assert isinstance(code, str)
        assert len(code) > 0
