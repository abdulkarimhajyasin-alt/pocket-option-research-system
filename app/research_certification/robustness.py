"""Research robustness engine."""

from __future__ import annotations

from app.research_certification.models import ResearchRobustnessScore
from app.research_certification.scoring import average, clamp


class ResearchRobustnessEngine:
    """Evaluate repeatability, variance, reliability, adaptability, and regime resilience."""

    def evaluate(self, inputs: dict[str, float]) -> ResearchRobustnessScore:
        repeatability = average(
            inputs.get("benchmark_score", 0),
            inputs.get("pattern_reliability", 0),
        )
        variance = clamp(
            100 - abs(inputs.get("benchmark_score", 0) - inputs.get("regime_score", 0))
        )
        reliability = average(
            inputs.get("signal_quality", 0),
            inputs.get("pattern_reliability", 0),
            inputs.get("lifecycle_quality", 0),
        )
        adaptability = average(inputs.get("pattern_adaptation", 0), inputs.get("regime_score", 0))
        regime_resilience = average(
            inputs.get("regime_score", 0),
            inputs.get("regime_stability", 0),
        )
        score = average(repeatability, variance, reliability, adaptability, regime_resilience)
        return ResearchRobustnessScore(
            score,
            repeatability,
            variance,
            reliability,
            adaptability,
            regime_resilience,
        )
