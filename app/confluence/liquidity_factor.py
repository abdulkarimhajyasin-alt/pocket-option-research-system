"""Liquidity context factor scoring."""

from __future__ import annotations

from typing import Any

from app.confluence.models import LiquidityFactorScore


class LiquidityFactorEngine:
    """Evaluate sweep quality, sweep confirmation, and liquidity context."""

    def evaluate(self, opportunity: dict[str, Any]) -> LiquidityFactorScore:
        liquidity = self._float(opportunity.get("liquidity_score"))
        factors = opportunity.get("supporting_factors", [])
        rejections = opportunity.get("rejection_factors", [])
        text = " ".join(str(item) for item in factors if isinstance(factors, list))
        rejected = " ".join(
            str(item) for item in rejections if isinstance(rejections, list)
        )
        sweep_confirmed = "سيولة" in text or "sweep" in text.lower()
        sweep_warning = "سيولة" in rejected
        confirmation = 85.0 if sweep_confirmed else 45.0
        context = 70.0 if not sweep_warning else 40.0
        score = round(liquidity * 0.45 + confirmation * 0.35 + context * 0.20, 2)
        strengths = []
        weaknesses = []
        warnings = []
        if sweep_confirmed:
            strengths.append("سياق السيولة مؤكد بحثيا")
        else:
            weaknesses.append("تأكيد السيولة غير كاف")
        if sweep_warning:
            warnings.append("تحذير من ضعف سياق السيولة")
        return LiquidityFactorScore(
            name="عامل السيولة",
            score=self._bound(score),
            explanation="تقييم بحثي لجودة السيولة وتأكيد السحب والسياق.",
            strengths=strengths,
            weaknesses=weaknesses,
            warnings=warnings,
            metrics={
                "liquidity_score": liquidity,
                "sweep_confirmation": confirmation,
                "liquidity_context": context,
            },
        )

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _bound(self, value: float) -> float:
        return max(0.0, min(100.0, value))
