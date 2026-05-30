"""Readiness scoring helpers."""

from __future__ import annotations


def readiness_state(score: float) -> str:
    """Return Arabic readiness state for a 0-100 score."""

    if score >= 95:
        return "جاهزة للأبحاث المتقدمة"
    if score >= 85:
        return "جاهزة بشروط"
    if score >= 70:
        return "تحتاج تحسين محدود"
    if score >= 50:
        return "تحتاج تحسين كبير"
    return "غير مؤهلة"


def bound(value: float) -> float:
    """Clamp score to 0-100."""

    return max(0.0, min(100.0, round(value, 2)))
