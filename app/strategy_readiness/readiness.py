"""Strategy readiness evaluation engine."""

from __future__ import annotations

from statistics import mean
from typing import Any

from app.strategy_readiness.models import StrategyReadinessScore
from app.strategy_readiness.scoring import bound, readiness_state


class StrategyReadinessEngine:
    """Evaluate the full research pipeline readiness."""

    def evaluate(self, inputs: dict[str, Any], stability_score: float) -> StrategyReadinessScore:
        components = {
            "جودة الإشارة": self._signal_quality(inputs),
            "اتساق الإشارة": self._signal_consistency(inputs),
            "دقة الثقة": self._confidence_accuracy(inputs),
            "جودة الفرصة": self._opportunity_quality(inputs),
            "جودة الأطر الزمنية": self._timeframe_quality(inputs),
            "جودة التوافق": self._confluence_quality(inputs),
            "جودة دورة الحياة": self._lifecycle_quality(inputs),
            "استقرار البحث": stability_score,
        }
        score = bound(mean(components.values()) if components else 0.0)
        return StrategyReadinessScore(
            score=score,
            state=readiness_state(score),
            explanation="تقييم نضج بحثي شامل وليس موافقة نشر أو تنفيذ.",
            components=components,
        )

    def _signal_quality(self, inputs: dict[str, Any]) -> float:
        summary = inputs.get("signal_summary", {})
        return self._float(summary.get("average_confidence"))

    def _signal_consistency(self, inputs: dict[str, Any]) -> float:
        summary = inputs.get("performance_summary", {})
        return self._float(summary.get("consistency_score"))

    def _confidence_accuracy(self, inputs: dict[str, Any]) -> float:
        summary = inputs.get("performance_summary", {})
        return self._float(summary.get("confidence_accuracy_score"))

    def _opportunity_quality(self, inputs: dict[str, Any]) -> float:
        summary = inputs.get("opportunity_summary", {})
        return self._float(summary.get("average_score"))

    def _timeframe_quality(self, inputs: dict[str, Any]) -> float:
        summary = inputs.get("timeframe_summary", {})
        return self._float(summary.get("average_alignment"))

    def _confluence_quality(self, inputs: dict[str, Any]) -> float:
        summary = inputs.get("confluence_summary", {})
        return self._float(summary.get("average_confluence"))

    def _lifecycle_quality(self, inputs: dict[str, Any]) -> float:
        summary = inputs.get("lifecycle_summary", {})
        return self._float(summary.get("average_quality"))

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
