"""Opportunity qualification factor scoring."""

from __future__ import annotations

from typing import Any

from app.confluence.models import OpportunityFactorScore


class OpportunityFactorEngine:
    """Evaluate opportunity score, qualification state, and rejection factors."""

    def evaluate(self, opportunity: dict[str, Any]) -> OpportunityFactorScore:
        base = self._float(opportunity.get("qualification_score"))
        rejection_factors = opportunity.get("rejection_factors", [])
        rejection_count = (
            len(rejection_factors) if isinstance(rejection_factors, list) else 0
        )
        state = str(opportunity.get("qualification_state", ""))
        state_bonus = 8.0 if "عالية" in state or "قوية" in state else 0.0
        penalty = min(20.0, rejection_count * 4.0)
        score = self._bound(round(base + state_bonus - penalty, 2))
        strengths = list(opportunity.get("strengths", []) or [])[:3]
        weaknesses = list(opportunity.get("weaknesses", []) or [])[:3]
        warnings = list(rejection_factors or [])[:3]
        if score >= 70:
            strengths.append("جودة الفرصة البحثية مرتفعة")
        else:
            weaknesses.append("تأهيل الفرصة غير مكتمل")
        return OpportunityFactorScore(
            name="عامل الفرصة",
            score=score,
            explanation="تقييم بحثي لجودة الفرصة وحالة التأهيل.",
            strengths=strengths,
            weaknesses=weaknesses,
            warnings=warnings,
            metrics={
                "opportunity_score": base,
                "rejection_count": rejection_count,
                "qualification_state": state,
            },
        )

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _bound(self, value: float) -> float:
        return max(0.0, min(100.0, value))
