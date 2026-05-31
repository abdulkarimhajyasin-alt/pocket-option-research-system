"""Shared scoring helpers for market observation."""

from __future__ import annotations


def clamp(value: float) -> float:
    """Clamp a score into the dashboard score range."""
    return round(max(0.0, min(100.0, value)), 2)


def average(values: list[float]) -> float:
    """Return a clamped average for optional score inputs."""
    if not values:
        return 0.0
    return clamp(sum(clamp(value) for value in values) / len(values))


def state_from_score(score: float) -> tuple[str, str]:
    """Return an Arabic research state for the canonical observation score."""
    if score >= 90:
        return "جاهزة كمصدر مراقبة موحد", "الملاحظات موحدة وكافية للتحليل البحثي."
    if score >= 75:
        return "صالحة مع مراجعة", "الملاحظات قابلة للاستخدام مع متابعة فجوات محدودة."
    if score >= 55:
        return "تحتاج تحسين", "المصدر الموحد يحتاج تغطية أو اتساقا أفضل قبل الاعتماد."
    return "غير كافية", "الملاحظات المتاحة لا تكفي كمصدر سوق موحد."
