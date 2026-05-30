"""Signal intelligence factor scoring."""

from __future__ import annotations

from typing import Any

from app.confluence.models import SignalFactorScore


class SignalFactorEngine:
    """Evaluate signal confidence, quality, and consistency."""

    def evaluate(
        self,
        opportunity: dict[str, Any],
        signal_summary: dict[str, Any],
    ) -> SignalFactorScore:
        confidence = self._float(opportunity.get("confidence"))
        quality = self._float(signal_summary.get("average_confidence"))
        consistency = self._float(signal_summary.get("classification_balance_score"))
        if consistency == 0:
            consistency = self._float(signal_summary.get("confidence_consistency"))
        score = round(confidence * 0.45 + quality * 0.35 + consistency * 0.20, 2)
        strengths = []
        weaknesses = []
        warnings = []
        if confidence >= 70:
            strengths.append("ثقة الإشارة مرتفعة")
        else:
            weaknesses.append("ثقة الإشارة تحتاج مراجعة")
        if quality >= 65:
            strengths.append("جودة الإشارة مستقرة")
        else:
            warnings.append("جودة الإشارة محدودة")
        return SignalFactorScore(
            name="عامل الإشارة",
            score=self._bound(score),
            explanation=("تقييم بحثي لثقة الإشارة وجودتها واتساقها."),
            strengths=strengths,
            weaknesses=weaknesses,
            warnings=warnings,
            metrics={
                "signal_confidence": confidence,
                "signal_quality": quality,
                "signal_consistency": consistency,
            },
        )

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _bound(self, value: float) -> float:
        return max(0.0, min(100.0, value))
