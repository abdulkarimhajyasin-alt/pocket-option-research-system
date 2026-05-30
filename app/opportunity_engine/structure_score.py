"""Market structure scoring for opportunity qualification."""

from __future__ import annotations

from app.opportunity_engine.models import ScoreBreakdown


class StructureScoreEngine:
    """Score HH/HL/LH/LL structure quality."""

    def score(self, signal: dict) -> ScoreBreakdown:
        structure = signal.get("structure", {})
        state = str(structure.get("state", ""))
        pattern = str(structure.get("pattern", ""))
        points = structure.get("points", {}) if isinstance(structure, dict) else {}
        score = 45.0
        strengths = []
        weaknesses = []
        if state in {"هيكل صاعد", "هيكل هابط"}:
            score += 35
            strengths.append("اتجاه هيكلي واضح")
        elif state == "هيكل انتقالي":
            score += 18
            weaknesses.append("الهيكل في مرحلة انتقالية")
        else:
            weaknesses.append("الهيكل عرضي")
        if pattern in {"HH/HL", "LH/LL"}:
            score += 15
            strengths.append(f"نمط هيكلي {pattern}")
        if points:
            score += 5
        return ScoreBreakdown(
            score=round(min(score, 100.0), 2),
            explanation=f"تقييم الهيكل السعري: {state or 'غير متاح'}",
            strengths=strengths,
            weaknesses=weaknesses,
        )
