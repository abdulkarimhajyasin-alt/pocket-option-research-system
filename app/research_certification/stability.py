"""Research stability engine."""

from __future__ import annotations

from app.research_certification.models import ResearchStabilityScore
from app.research_certification.scoring import average


class ResearchStabilityEngine:
    """Evaluate score, quality, confidence, pattern, and regime stability."""

    def evaluate(self, inputs: dict[str, float]) -> ResearchStabilityScore:
        score_stability = average(
            inputs.get("readiness_stability", 0),
            inputs.get("benchmark_stability", 0),
        )
        quality_stability = average(
            inputs.get("signal_quality", 0),
            inputs.get("opportunity_quality", 0),
            inputs.get("lifecycle_quality", 0),
        )
        confidence_stability = average(
            inputs.get("confidence_accuracy", 0),
            inputs.get("confluence_quality", 0),
        )
        pattern_stability = inputs.get("pattern_stability", 0)
        regime_stability = inputs.get("regime_stability", 0)
        score = average(
            score_stability,
            quality_stability,
            confidence_stability,
            pattern_stability,
            regime_stability,
        )
        return ResearchStabilityScore(
            score,
            score_stability,
            quality_stability,
            confidence_stability,
            pattern_stability,
            regime_stability,
        )
