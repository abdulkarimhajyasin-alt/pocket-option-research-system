"""Entry analysis for research lifecycle simulation."""

from __future__ import annotations

from typing import Any

from app.trade_lifecycle.models import EntryAnalysis


class EntryAnalysisEngine:
    """Evaluate entry timing, confirmation quality, alignment, and readiness."""

    def evaluate(self, decision: dict[str, Any]) -> EntryAnalysis:
        confluence = decision.get("confluence", {})
        factors = confluence.get("factors", []) if isinstance(confluence, dict) else []
        factor_scores = [
            self._float(factor.get("score"))
            for factor in factors
            if isinstance(factor, dict)
        ]
        confirmation_quality = self._factor_score(factors, "عامل الأطر الزمنية")
        session_quality = self._factor_score(factors, "عامل الجلسة")
        confluence_score = self._float(decision.get("confluence_score"))
        timing = round((session_quality * 0.55 + confluence_score * 0.45), 2)
        alignment = round((confirmation_quality + confluence_score) / 2, 2)
        average_factor = sum(factor_scores) / len(factor_scores) if factor_scores else 0.0
        readiness = round(timing * 0.30 + alignment * 0.35 + average_factor * 0.35, 2)
        return EntryAnalysis(
            timing_quality=self._bound(timing),
            confirmation_quality=self._bound(confirmation_quality),
            entry_alignment=self._bound(alignment),
            readiness_score=self._bound(readiness),
            explanation="تقييم بحثي لجودة توقيت الدخول وتوافق التأكيد.",
        )

    def _factor_score(self, factors: Any, name: str) -> float:
        if not isinstance(factors, list):
            return 0.0
        for factor in factors:
            if isinstance(factor, dict) and factor.get("name") == name:
                return self._float(factor.get("score"))
        return 0.0

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _bound(self, value: float) -> float:
        return max(0.0, min(100.0, value))
