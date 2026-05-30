"""Multi-timeframe confirmation factor scoring."""

from __future__ import annotations

from typing import Any

from app.confluence.models import TimeframeFactorScore


class TimeframeFactorEngine:
    """Evaluate alignment score, confirmation state, and conflict state."""

    def evaluate(self, confirmation: dict[str, Any]) -> TimeframeFactorScore:
        alignment = self._float(confirmation.get("confirmation_score"))
        state = str(confirmation.get("confirmation_state", ""))
        conflict = confirmation.get("conflict", {})
        has_conflict = (
            bool(conflict.get("has_conflict")) if isinstance(conflict, dict) else False
        )
        state_bonus = 8.0 if state in {"مؤكد بقوة", "مؤكد"} else 0.0
        conflict_penalty = 18.0 if has_conflict else 0.0
        score = self._bound(round(alignment + state_bonus - conflict_penalty, 2))
        strengths = list(confirmation.get("supporting_factors", []) or [])[:3]
        weaknesses = list(confirmation.get("conflicting_factors", []) or [])[:3]
        warnings = []
        if has_conflict:
            warnings.append("يوجد تعارض بين الأطر الزمنية")
        return TimeframeFactorScore(
            name="عامل الأطر الزمنية",
            score=score,
            explanation=("تقييم بحثي لتوافق الأطر الزمنية وحالة التعارض."),
            strengths=strengths,
            weaknesses=weaknesses,
            warnings=warnings,
            metrics={
                "alignment_score": alignment,
                "confirmation_state": state,
                "has_conflict": has_conflict,
            },
        )

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _bound(self, value: float) -> float:
        return max(0.0, min(100.0, value))
