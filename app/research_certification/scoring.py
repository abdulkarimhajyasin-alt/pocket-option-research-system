"""Shared scoring helpers for certification."""

from __future__ import annotations

from typing import Any


def clamp(value: Any) -> float:
    """Clamp a numeric value to 0-100."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return round(max(0.0, min(100.0, number)), 2)


def average(*values: float) -> float:
    """Average 0-100 scores."""
    numbers = [clamp(value) for value in values]
    return round(sum(numbers) / len(numbers), 2) if numbers else 0.0


def certification_state(score: float) -> str:
    """Return Arabic certification state."""
    if score >= 95:
        return "معتمدة للأبحاث المتقدمة"
    if score >= 85:
        return "جاهزة بشروط"
    if score >= 70:
        return "تحتاج تحسين محدود"
    if score >= 50:
        return "تحتاج تحسين كبير"
    return "غير مؤهلة"
