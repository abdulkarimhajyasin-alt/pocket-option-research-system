"""Arabic display formatting helpers for dashboard templates."""

from __future__ import annotations

from datetime import UTC, datetime
from math import isfinite
from typing import Any


UNAVAILABLE = "غير متوفر"


def parse_datetime(value: Any) -> datetime | None:
    """Parse dashboard timestamps into timezone-aware datetimes when possible."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if value in (None, "", "n/a"):
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        normalized = text.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def format_datetime(value: Any, include_time: bool = True) -> str:
    """Format a date/time for Arabic dashboard display."""
    parsed = parse_datetime(value)
    if parsed is None:
        return UNAVAILABLE
    local = parsed.astimezone()
    pattern = "%d-%m-%Y %H:%M" if include_time else "%d-%m-%Y"
    return local.strftime(pattern)


def format_relative_time(value: Any, now: datetime | None = None) -> str:
    """Return a compact Arabic relative timestamp."""
    parsed = parse_datetime(value)
    if parsed is None:
        return UNAVAILABLE
    reference = now or datetime.now(parsed.tzinfo or UTC)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=UTC)
    seconds = max(0, int((reference - parsed).total_seconds()))
    minutes = seconds // 60
    if minutes < 1:
        return "منذ أقل من دقيقة"
    if minutes < 60:
        return f"منذ {minutes} دقيقة"
    hours = minutes // 60
    if hours < 24:
        return f"منذ {hours} ساعة"
    days = hours // 24
    return f"منذ {days} يوم"


def format_number(value: Any, decimals: int = 2) -> str:
    """Format a dashboard number without noisy floating point artifacts."""
    number = _coerce_number(value)
    if number is None:
        return UNAVAILABLE
    if number == int(number):
        return str(int(number))
    return f"{number:.{decimals}f}"


def format_percent(value: Any, decimals: int = 0) -> str:
    """Format an already-0-to-100 score as a percentage."""
    number = _coerce_number(value)
    if number is None:
        return UNAVAILABLE
    if number == int(number):
        return f"{int(number)}%"
    return f"{number:.{decimals}f}%"


def format_metric(value: Any) -> str:
    """Format a generic metric value for user-facing cards."""
    if isinstance(value, str):
        parsed = parse_datetime(value)
        if parsed is not None:
            return format_datetime(parsed)
        if value.strip().lower() in {"n/a", "none", "null", ""}:
            return UNAVAILABLE
        return value
    if isinstance(value, bool):
        return "نعم" if value else "لا"
    return format_number(value)


def format_duration(start: Any, end: Any | None = None) -> str:
    """Format duration between two timestamps."""
    parsed_start = parse_datetime(start)
    parsed_end = parse_datetime(end) if end is not None else datetime.now(UTC)
    if parsed_start is None or parsed_end is None:
        return UNAVAILABLE
    seconds = max(0, int((parsed_end - parsed_start).total_seconds()))
    if seconds < 60:
        return f"{seconds} ثانية"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} دقيقة"
    hours = minutes // 60
    return f"{hours} ساعة و{minutes % 60} دقيقة"


def _coerce_number(value: Any) -> float | None:
    if value in (None, "", "n/a"):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(number):
        return None
    return round(number, 10)
