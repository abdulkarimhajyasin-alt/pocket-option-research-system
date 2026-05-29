"""Small deterministic statistics helpers for validation modules."""

from __future__ import annotations


def mean(values: list[float]) -> float:
    """Return arithmetic mean, or zero for an empty input."""
    return sum(values) / len(values) if values else 0.0


def population_stdev(values: list[float]) -> float:
    """Return population standard deviation, or zero for less than two values."""
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return (sum((value - avg) ** 2 for value in values) / len(values)) ** 0.5


def coefficient_of_variation(values: list[float]) -> float:
    """Return absolute coefficient of variation."""
    avg = abs(mean(values))
    return population_stdev(values) / avg if avg else 0.0


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Clamp a value to a numeric range."""
    return max(minimum, min(maximum, value))
