"""Validation, confidence, and quality engines for unified observations."""

from __future__ import annotations

from app.observation_intelligence.models import AggregationResult
from app.observation_intelligence.models import ConfidenceResult
from app.observation_intelligence.models import QualityResult
from app.observation_intelligence.models import UnifiedObservation
from app.observation_intelligence.models import ValidationResult
from app.observation_intelligence.scoring import average
from app.observation_intelligence.scoring import clamp


class ObservationValidationEngine:
    """Validate normalized structure, compatibility, completeness, consistency, integrity."""

    def validate(
        self,
        observations: tuple[UnifiedObservation, ...],
        aggregation: AggregationResult,
    ) -> ValidationResult:
        count = len(observations)
        structure = 100.0 if count else 0.0
        compatibility = min(100.0, len({item.source_type for item in observations}) * 20.0)
        completeness = aggregation.completeness
        consistency = aggregation.consistency
        integrity = average([item.quality_score for item in observations])
        return ValidationResult(
            score=average([structure, compatibility, completeness, consistency, integrity]),
            normalized_structure=clamp(structure),
            source_compatibility=clamp(compatibility),
            completeness=clamp(completeness),
            consistency=clamp(consistency),
            integrity=clamp(integrity),
        )


class ObservationConfidenceEngine:
    """Evaluate source, data, visibility, and consistency confidence."""

    def evaluate(
        self,
        observations: tuple[UnifiedObservation, ...],
        aggregation: AggregationResult,
    ) -> ConfidenceResult:
        source_confidence = min(100.0, len({item.source_type for item in observations}) * 20.0)
        data_confidence = average([item.confidence_score for item in observations])
        visibility_confidence = aggregation.visibility
        consistency_confidence = aggregation.consistency
        return ConfidenceResult(
            score=average(
                [
                    source_confidence,
                    data_confidence,
                    visibility_confidence,
                    consistency_confidence,
                ]
            ),
            source_confidence=clamp(source_confidence),
            data_confidence=clamp(data_confidence),
            visibility_confidence=clamp(visibility_confidence),
            consistency_confidence=clamp(consistency_confidence),
        )


class ObservationQualityEngine:
    """Evaluate visibility, completeness, consistency, freshness, and reliability."""

    def evaluate(
        self,
        observations: tuple[UnifiedObservation, ...],
        aggregation: AggregationResult,
        validation: ValidationResult,
    ) -> QualityResult:
        visibility = aggregation.visibility
        completeness = aggregation.completeness
        consistency = aggregation.consistency
        freshness = 100.0 if all(item.timestamp for item in observations) else 70.0
        reliability = average(
            [validation.score, aggregation.confidence, aggregation.coverage]
        )
        return QualityResult(
            score=average([visibility, completeness, consistency, freshness, reliability]),
            visibility=clamp(visibility),
            completeness=clamp(completeness),
            consistency=clamp(consistency),
            freshness=clamp(freshness),
            reliability=clamp(reliability),
        )
