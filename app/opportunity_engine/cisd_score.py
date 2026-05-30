"""CISD scoring for opportunity qualification."""

from __future__ import annotations

from app.opportunity_engine.models import ScoreBreakdown


class CISDScoreEngine:
    """Score bullish/bearish CISD quality, validation, and recency."""

    def score(self, signal: dict) -> ScoreBreakdown:
        cisd = signal.get("cisd", {}) or {}
        direction = str(cisd.get("direction", "محايد"))
        validated = bool(cisd.get("validated"))
        contribution = float(cisd.get("confidence_contribution", 0.0) or 0.0)
        score = 30.0 + contribution * 30.0
        strengths = []
        weaknesses = []
        if validated:
            score += 30
            strengths.append(f"CISD {direction} مؤكد")
        else:
            weaknesses.append("CISD غير مؤكد")
        if direction in {"صاعد", "هابط"}:
            score += 10
        return ScoreBreakdown(
            score=round(min(score, 100.0), 2),
            explanation=f"تقييم تغير الحالة: {direction}",
            strengths=strengths,
            weaknesses=weaknesses,
        )
