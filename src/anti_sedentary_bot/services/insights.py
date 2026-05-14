from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from ..db.models import User
from ..i18n import t
from ..repositories import tasks as task_repo
from ..utils.time import now, parse_hhmm, to_tz

_BAR_CHARS = " ▁▂▃▄▅▆▇█"


def _bar_char(value: float, max_value: float) -> str:
    if max_value <= 0:
        return _BAR_CHARS[0]
    idx = round(value / max_value * (len(_BAR_CHARS) - 1))
    return _BAR_CHARS[max(0, min(idx, len(_BAR_CHARS) - 1))]


def _build_heatmap_bar(hourly_completed: dict[int, int], start_h: int, end_h: int) -> str:
    """Return a single-line bar chart for hours in [start_h, end_h)."""
    if start_h >= end_h:
        hours = list(range(start_h, 24)) + list(range(0, end_h))
    else:
        hours = list(range(start_h, end_h))

    if not hours:
        return ""

    max_val = max((hourly_completed.get(h, 0) for h in hours), default=0)
    bars = "".join(_bar_char(hourly_completed.get(h, 0), max_val) for h in hours)
    label_start = f"{hours[0]:02d}h"
    label_end = f"{hours[-1]:02d}h"
    return f"{label_start} {bars} {label_end}"


def _classify_trend(first_half_mean: float, second_half_mean: float, locale: str) -> str:
    delta = second_half_mean - first_half_mean
    if delta < -0.3:
        return t(locale, "insights.easier")
    if delta > 0.3:
        return t(locale, "insights.harder")
    return t(locale, "insights.same")


async def build_insights(user: User, days: int = 14) -> str:
    locale = user.language
    cutoff = now() - timedelta(days=days)

    # Fetch completed tasks in window
    completed_tasks = await task_repo.completed_in_window(user, cutoff)

    # Fetch skipped/failed tasks
    failed_skipped = await task_repo.failed_skipped_in_window(user, cutoff)

    if not completed_tasks and not failed_skipped:
        return t(locale, "insights.header") + "\n\n" + t(locale, "insights.no_data")

    # Build hourly buckets
    hourly_completed: dict[int, int] = defaultdict(int)
    exercise_hours: dict[str, list[int]] = defaultdict(list)

    for completed_at, exercise_code in completed_tasks:
        local = to_tz(completed_at)
        hourly_completed[local.hour] += 1
        exercise_hours[exercise_code].append(local.hour)

    hourly_failed: dict[int, int] = defaultdict(int)
    for ts in failed_skipped:
        local = to_tz(ts)
        hourly_failed[local.hour] += 1

    # Parse user work window
    try:
        start_h = parse_hhmm(user.day_start).hour
        end_h = parse_hhmm(user.day_end).hour
    except Exception:
        start_h, end_h = 9, 18

    bar = _build_heatmap_bar(dict(hourly_completed), start_h, end_h)

    # Best / worst hour (within window)
    if start_h >= end_h:
        window_hours = list(range(start_h, 24)) + list(range(0, end_h))
    else:
        window_hours = list(range(start_h, end_h))

    best_hour: int | None = None
    worst_hour: int | None = None
    if window_hours:
        best_hour = max(window_hours, key=lambda h: hourly_completed.get(h, 0))
        worst_hour = max(window_hours, key=lambda h: hourly_failed.get(h, 0))

    lines: list[str] = [t(locale, "insights.header"), ""]
    if bar:
        lines.append(bar)
        lines.append("")
    if best_hour is not None:
        lines.append(t(locale, "insights.best_hour", hour=f"{best_hour:02d}:00"))
    if worst_hour is not None:
        lines.append(t(locale, "insights.worst_hour", hour=f"{worst_hour:02d}:00"))

    # Per-exercise difficulty trends
    trend_lines: list[str] = []

    # Find exercise codes with >= 5 completions in last 30 days
    exercise_counts: dict[str, int] = defaultdict(int)
    for _, code in completed_tasks:
        exercise_counts[code] += 1

    for code, count in exercise_counts.items():
        if count < 5:
            continue
        # Re-fetch recent tasks for this exercise over 30d to get timestamps
        recent_tasks = await task_repo.recent_completions_by_code(user, code, limit=10)
        if len(recent_tasks) < 4:
            continue
        # Use snooze_count as a proxy for difficulty (higher = harder)
        # Since we don't store explicit difficulty ratings, use nudge_count + snooze_count
        ratings = [float(tk.nudge_count + tk.snooze_count) for tk in recent_tasks]
        mid = len(ratings) // 2
        first_half = ratings[mid:]  # oldest first due to order_by -completed_at
        second_half = ratings[:mid]
        first_mean = sum(first_half) / len(first_half) if first_half else 0.0
        second_mean = sum(second_half) / len(second_half) if second_half else 0.0
        trend = _classify_trend(first_mean, second_mean, locale)
        # Get display name from the first task
        display_name = recent_tasks[0].title if recent_tasks else code
        trend_lines.append(f"• {display_name}: {trend}")

    if trend_lines:
        lines.append("")
        lines.append(t(locale, "insights.trends_header"))
        lines.extend(trend_lines)

    return "\n".join(lines)
