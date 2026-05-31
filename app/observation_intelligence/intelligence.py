"""Unified observation intelligence engine."""

from __future__ import annotations

from app.observation_intelligence.models import AggregationResult
from app.observation_intelligence.models import ConfidenceResult
from app.observation_intelligence.models import IntelligenceResult
from app.observation_intelligence.models import QualityResult
from app.observation_intelligence.models import ValidationResult
from app.observation_intelligence.scoring import average
from app.observation_intelligence.scoring import observation_state


class ObservationIntelligenceEngine:
    """Generate observation quality, confidence, reliability, completeness, readiness."""

    def evaluate(
        self,
        aggregation: AggregationResult,
        validation: ValidationResult,
        confidence: ConfidenceResult,
        quality: QualityResult,
    ) -> IntelligenceResult:
        reliability = average([validation.score, quality.reliability, confidence.score])
        readiness = average(
            [aggregation.score, validation.score, confidence.score, quality.score]
        )
        score = average(
            [
                quality.score,
                confidence.score,
                reliability,
                aggregation.completeness,
                readiness,
            ]
        )
        state, explanation = observation_state(score)
        return IntelligenceResult(
            score=score,
            state=state,
            explanation=explanation,
            observation_quality=quality.score,
            observation_confidence=confidence.score,
            observation_reliability=reliability,
            observation_completeness=aggregation.completeness,
            observation_readiness=readiness,
        )
