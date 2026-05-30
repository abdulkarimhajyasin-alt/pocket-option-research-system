"""Signal performance factor scoring."""

from __future__ import annotations

from typing import Any

from app.confluence.models import PerformanceFactorScore


class PerformanceFactorEngine:
    """Evaluate win rate, stability, consistency, and confidence accuracy."""

    def evaluate(self, performance_summary: dict[str, Any]) -> PerformanceFactorScore:
        win_rate = self._float(performance_summary.get("win_rate")) * 100
        stability = self._float(performance_summary.get("stability_score"))
        consistency = self._float(performance_summary.get("consistency_score"))
        confidence_accuracy = self._float(
            performance_summary.get("confidence_accuracy_score")
        )
        score = round(
            win_rate * 0.30
            + stability * 0.25
            + consistency * 0.25
            + confidence_accuracy * 0.20,
            2,
        )
        strengths = []
        weaknesses = []
        warnings = []
        if win_rate >= 55:
            strengths.append("نتائج الأداء البحثي داعمة")
        else:
            warnings.append("الأداء التاريخي البحثي غير كاف")
        if stability >= 65:
            strengths.append("استقرار الأداء مقبول")
        else:
            weaknesses.append("استقرار الأداء يحتاج تحسين")
        return PerformanceFactorScore(
            name="عامل الأداء",
            score=self._bound(score),
            explanation=("تقييم بحثي للأداء والاستقرار ودقة الثقة."),
            strengths=strengths,
            weaknesses=weaknesses,
            warnings=warnings,
            metrics={
                "win_rate": round(win_rate, 2),
                "stability": stability,
                "consistency": consistency,
                "confidence_accuracy": confidence_accuracy,
            },
        )

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _bound(self, value: float) -> float:
        return max(0.0, min(100.0, value))
