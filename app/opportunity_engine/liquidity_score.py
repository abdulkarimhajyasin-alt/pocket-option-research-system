"""Liquidity scoring for opportunity qualification."""

from __future__ import annotations

from app.opportunity_engine.models import ScoreBreakdown


class LiquidityScoreEngine:
    """Score liquidity sweeps, confirmation, freshness, and nearby liquidity."""

    def score(self, signal: dict) -> ScoreBreakdown:
        liquidity = signal.get("liquidity", {}) or {}
        direction = str(liquidity.get("sweep_direction", ""))
        confirmed = bool(liquidity.get("sweep_confirmed"))
        score = 35.0
        strengths = []
        weaknesses = []
        if confirmed:
            score += 45
            strengths.append(direction)
            strengths.append("تأكيد سحب السيولة")
        else:
            weaknesses.append("سحب السيولة غير مؤكد")
        if direction and direction != "لا يوجد سحب":
            score += 10
        else:
            weaknesses.append("لا توجد سيولة قريبة مؤكدة")
        return ScoreBreakdown(
            score=round(min(score, 100.0), 2),
            explanation="تقييم السيولة يعتمد على السحب والتأكيد والقرب.",
            strengths=strengths,
            weaknesses=weaknesses,
        )
