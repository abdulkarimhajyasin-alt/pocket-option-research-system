"""Shared scoring helpers for observation intelligence."""

from __future__ import annotations


def clamp(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(clamp(value) for value in values) / len(values), 2)


def observation_state(score: float) -> tuple[str, str]:
    if score >= 95:
        return "جاهزة للتحليل المتقدم", "الملاحظات موحدة وجاهزة للتحليل المتقدم."
    if score >= 85:
        return "جيدة بشروط", "الملاحظات موحدة مع تحسينات محدودة مطلوبة."
    if score >= 70:
        return "تحتاج تحسين محدود", "الملاحظات قابلة للتحليل مع فجوات محدودة."
    if score >= 50:
        return "تحتاج تحسين كبير", "الملاحظات تحتاج تحسينات قبل الاعتماد."
    return "غير مؤهلة", "الملاحظات غير كافية للتحليل الموحد."
