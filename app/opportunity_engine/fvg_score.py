"""FVG scoring for opportunity qualification."""

from __future__ import annotations

from app.opportunity_engine.models import ScoreBreakdown


class FVGScoreEngine:
    """Score FVG freshness, size, distance, and mitigation."""

    def score(self, signal: dict) -> ScoreBreakdown:
        fvg = signal.get("fvg")
        if not isinstance(fvg, dict):
            return ScoreBreakdown(
                score=20.0,
                explanation="لا توجد فجوة قيمة عادلة حديثة.",
                weaknesses=["غياب FVG"],
            )
        freshness = float(fvg.get("freshness_score", 0.0) or 0.0)
        gap_size = float(fvg.get("gap_size", 0.0) or 0.0)
        distance = float(fvg.get("distance_from_price", 0.0) or 0.0)
        mitigated = bool(fvg.get("mitigated"))
        score = 35.0 + freshness * 35.0
        strengths = [f"FVG {fvg.get('direction', 'غير متاح')}"]
        weaknesses = []
        if gap_size > 0:
            score += 12
            strengths.append("حجم الفجوة قابل للقياس")
        if distance <= max(gap_size * 2, 0.00001):
            score += 10
            strengths.append("السعر قريب من منطقة الفجوة")
        if mitigated:
            score -= 12
            weaknesses.append("الفجوة مخففة جزئيا")
        return ScoreBreakdown(
            score=round(max(0.0, min(score, 100.0)), 2),
            explanation="تقييم FVG يعتمد على الحداثة والحجم والقرب والتخفيف.",
            strengths=strengths,
            weaknesses=weaknesses,
        )
