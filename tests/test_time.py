"""Unit tests for anti_sedentary_bot.utils.time — pure functions only."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from anti_sedentary_bot.utils.time import (
    in_quiet_hours,
    in_work_window,
    parse_hhmm,
    work_window_bounds,
)

TZ = ZoneInfo("Europe/Amsterdam")


# ---------------------------------------------------------------------------
# parse_hhmm
# ---------------------------------------------------------------------------


def test_parse_hhmm_basic():
    t = parse_hhmm("09:30")
    assert t.hour == 9
    assert t.minute == 30


def test_parse_hhmm_midnight():
    t = parse_hhmm("00:00")
    assert t.hour == 0
    assert t.minute == 0


def test_parse_hhmm_strips_whitespace():
    t = parse_hhmm("  11:00  ")
    assert t.hour == 11
    assert t.minute == 0


# ---------------------------------------------------------------------------
# in_work_window — normal (non-crossing) window
# ---------------------------------------------------------------------------


def _dt(hour: int, minute: int = 0) -> datetime:
    """Create a timezone-aware datetime for today in Amsterdam."""
    from datetime import date

    d = date.today()
    return datetime(d.year, d.month, d.day, hour, minute, tzinfo=TZ)


def test_in_work_window_inside():
    assert in_work_window("09:00", "17:00", _dt(12)) is True


def test_in_work_window_before():
    assert in_work_window("09:00", "17:00", _dt(8)) is False


def test_in_work_window_after():
    assert in_work_window("09:00", "17:00", _dt(18)) is False


def test_in_work_window_on_start_boundary():
    assert in_work_window("09:00", "17:00", _dt(9, 0)) is True


def test_in_work_window_on_end_boundary():
    assert in_work_window("09:00", "17:00", _dt(17, 0)) is True


# ---------------------------------------------------------------------------
# in_work_window — crossing midnight
# ---------------------------------------------------------------------------


def test_in_work_window_midnight_crossing_inside_before_midnight():
    # Window 22:00–06:00; moment at 23:00 → inside
    assert in_work_window("22:00", "06:00", _dt(23)) is True


def test_in_work_window_midnight_crossing_inside_after_midnight():
    # Window 22:00–06:00; moment at 02:00 → inside
    assert in_work_window("22:00", "06:00", _dt(2)) is True


def test_in_work_window_midnight_crossing_outside():
    # Window 22:00–06:00; moment at 10:00 → outside
    assert in_work_window("22:00", "06:00", _dt(10)) is False


# ---------------------------------------------------------------------------
# work_window_bounds
# ---------------------------------------------------------------------------


def test_work_window_bounds_normal():
    from datetime import date

    d = date(2024, 6, 15)
    start, end = work_window_bounds("09:00", "17:00", d)
    assert start.hour == 9
    assert end.hour == 17
    assert start.date() == d
    assert end.date() == d


def test_work_window_bounds_crossing_midnight():
    from datetime import date, timedelta

    d = date(2024, 6, 15)
    start, end = work_window_bounds("22:00", "06:00", d)
    assert end.date() == d + timedelta(days=1)


# ---------------------------------------------------------------------------
# in_quiet_hours
# ---------------------------------------------------------------------------


def test_in_quiet_hours_none_none_returns_false():
    assert in_quiet_hours(None, None) is False


def test_in_quiet_hours_partial_none_returns_false():
    assert in_quiet_hours("22:00", None) is False
    assert in_quiet_hours(None, "06:00") is False


def test_in_quiet_hours_inside_window():
    assert in_quiet_hours("22:00", "06:00", _dt(23)) is True


def test_in_quiet_hours_outside_window():
    assert in_quiet_hours("22:00", "06:00", _dt(10)) is False
