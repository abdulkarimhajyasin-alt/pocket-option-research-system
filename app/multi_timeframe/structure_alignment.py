"""Structure alignment across supported timeframes."""

from __future__ import annotations

from app.multi_timeframe.models import StructureAlignmentResult, TimeframeState


class StructureAlignmentEngine:
    """Evaluate M1/M5/M15/H1 structural agreement."""

    pairs = (("M1", "M5"), ("M5", "M15"), ("M15", "H1"))

    def evaluate(self, states: list[TimeframeState]) -> StructureAlignmentResult:
        by_timeframe = {state.timeframe: state for state in states}
        pair_scores = {}
        for left, right in self.pairs:
            pair_scores[f"{left}-{right}"] = self._pair_score(
                by_timeframe[left],
                by_timeframe[right],
            )
        full_score = round(sum(pair_scores.values()) / len(pair_scores), 2)
        if full_score >= 90:
            state, state_ar = "fully_aligned", "متوافق بالكامل"
        elif full_score >= 70:
            state, state_ar = "mostly_aligned", "متوافق غالبا"
        elif full_score >= 45:
            state, state_ar = "mixed", "مختلط"
        else:
            state, state_ar = "conflicting", "متعارض"
        return StructureAlignmentResult(
            state=state,
            state_ar=state_ar,
            pair_scores=pair_scores,
            full_alignment_score=full_score,
            explanation=f"درجة توافق الهيكل عبر الأطر الزمنية {full_score:.2f}.",
        )

    def _pair_score(self, left: TimeframeState, right: TimeframeState) -> float:
        if left.state == right.state:
            return round((left.confidence + right.confidence) / 2, 2)
        if "محايد" in {left.state, right.state} or "انتقالي" in {left.state, right.state}:
            return 55.0
        return 20.0
