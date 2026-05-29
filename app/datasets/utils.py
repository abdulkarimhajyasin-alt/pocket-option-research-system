"""Shared dataset utility functions."""

from __future__ import annotations

from datetime import UTC, datetime


def parse_timeframe_seconds(timeframe: str) -> int:
    """Convert a normalized timeframe string into seconds."""
    cleaned = timeframe.strip().lower()
    if cleaned.endswith("m"):
        return int(cleaned[:-1]) * 60
    if cleaned.endswith("h"):
        return int(cleaned[:-1]) * 3600
    if cleaned.endswith("d"):
        return int(cleaned[:-1]) * 86400
    raise ValueError(f"Unsupported timeframe: {timeframe}")


def stable_datetime(value: datetime | None) -> str:
    """Return a stable timestamp string for deterministic hashing."""
    if value is None:
        return ""
    return value.astimezone(UTC).isoformat()
