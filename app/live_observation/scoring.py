"""Scoring helpers for live observation replay."""

from __future__ import annotations


def clamp(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def average(values: list[float]) -> float:
    if not values:
        return 0.0
    return clamp(sum(clamp(value) for value in values) / len(values))
