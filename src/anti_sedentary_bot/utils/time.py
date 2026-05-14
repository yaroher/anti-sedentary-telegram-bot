from __future__ import annotations

from datetime import date, datetime, time, timedelta

from ..config import settings


def now() -> datetime:
    return datetime.now(settings.tz)


def to_tz(dt: datetime) -> datetime:
    return dt.astimezone(settings.tz)


def today() -> date:
    return now().date()


def parse_hhmm(value: str) -> time:
    hour, minute = value.strip().split(":")
    return time(int(hour), int(minute))


def in_work_window(day_start: str, day_end: str, moment: datetime | None = None) -> bool:
    moment = moment or now()
    start = parse_hhmm(day_start)
    end = parse_hhmm(day_end)
    t = moment.time().replace(second=0, microsecond=0)
    if start <= end:
        return start <= t <= end
    return t >= start or t <= end


def work_window_bounds(day_start: str, day_end: str, d: date | None = None) -> tuple[datetime, datetime]:
    d = d or today()
    start_dt = datetime.combine(d, parse_hhmm(day_start), settings.tz)
    end_dt = datetime.combine(d, parse_hhmm(day_end), settings.tz)
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    return start_dt, end_dt


def in_quiet_hours(quiet_start: str | None, quiet_end: str | None, moment: datetime | None = None) -> bool:
    """Return True if the current moment falls inside the quiet window.

    Uses the same half-open interval logic as in_work_window.
    Returns False when quiet hours are not configured.
    """
    if not quiet_start or not quiet_end:
        return False
    return in_work_window(quiet_start, quiet_end, moment)


def human_time_left(unlock_at: datetime) -> str:
    delta = max(0, int((unlock_at - now()).total_seconds()))
    minutes, seconds = divmod(delta, 60)
    if minutes:
        return f"{minutes} мин {seconds:02d} сек"
    return f"{seconds} сек"
