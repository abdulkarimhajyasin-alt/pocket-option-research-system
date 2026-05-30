"""Trend alignment scoring."""

from __future__ import annotations

from collections import Counter

from app.multi_timeframe.models import TimeframeState, TrendAlignmentResult


class TrendAlignmentEngine:
    """Evaluate directional agreement, strength, and consistency."""

    def evaluate(self, states: list[TimeframeState]) -> TrendAlignmentResult:
        counts = Counter(state.state for state in states)
        dominant_count = max(counts.values()) if counts else 0
        directional = round((dominant_count / len(states)) * 100, 2) if states else 0.0
        strength = round(sum(state.confidence for state in states) / len(states), 2)
        consistency = round((directional * 0.65 + strength * 0.35), 2)
        score = round((directional + strength + consistency) / 3, 2)
        return TrendAlignmentResult(
            score=score,
            directional_agreement=directional,
            trend_strength=strength,
            trend_consistency=consistency,
            explanation=f"اتفاق الاتجاه {directional:.2f} مع قوة {strength:.2f}.",
        )
