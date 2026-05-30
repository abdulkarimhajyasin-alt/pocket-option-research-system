"""Expiry analysis for research lifecycle simulation."""

from __future__ import annotations

from typing import Any

from app.trade_lifecycle.models import ExpiryAnalysis


class ExpiryAnalysisEngine:
    """Evaluate deterministic expiry suitability for research windows."""

    SUPPORTED_EXPIRIES = ("30 ثانية", "1 دقيقة", "2 دقيقة", "3 دقائق", "5 دقائق")

    def evaluate(self, decision: dict[str, Any], entry_quality: float) -> ExpiryAnalysis:
        score = self._float(decision.get("confluence_score"))
        expiry = self._expiry(score, entry_quality)
        sensitivity = round(max(10.0, 100.0 - abs(score - entry_quality)), 2)
        suitability = round(score * 0.45 + entry_quality * 0.35 + sensitivity * 0.20, 2)
        quality = round(suitability * 0.75 + sensitivity * 0.25, 2)
        return ExpiryAnalysis(
            expiry=expiry,
            suitability=self._bound(suitability),
            outcome_sensitivity=self._bound(sensitivity),
            expiry_quality=self._bound(quality),
            explanation="تحليل بحثي لنافذة الانتهاء دون أي تنفيذ.",
        )

    def _expiry(self, score: float, entry_quality: float) -> str:
        average = (score + entry_quality) / 2
        if average >= 85:
            return "1 دقيقة"
        if average >= 75:
            return "2 دقيقة"
        if average >= 60:
            return "3 دقائق"
        if average >= 45:
            return "5 دقائق"
        return "30 ثانية"

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _bound(self, value: float) -> float:
        return max(0.0, min(100.0, value))
