"""Aggregate unified observations."""

from __future__ import annotations

from collections import Counter

from app.observation_intelligence.models import AggregationResult
from app.observation_intelligence.models import UnifiedObservation
from app.observation_intelligence.scoring import average
from app.observation_intelligence.scoring import clamp


class ObservationAggregator:
    """Merge observations and compute coverage, consistency, visibility, confidence."""

    def aggregate(
        self,
        observations: tuple[UnifiedObservation, ...],
    ) -> AggregationResult:
        count = len(observations)
        source_counts = Counter(item.source_type for item in observations)
        conflicts = sum(1 for value in source_counts.values() if value > 1)
        coverage = min(100.0, count * 20.0)
        consistency = 100.0 if conflicts == 0 else max(0.0, 100.0 - conflicts * 20.0)
        visibility = average([item.visibility_score for item in observations])
        completeness = average(
            [
                average(
                    [
                        item.assets,
                        item.payouts,
                        item.sessions,
                        item.symbols,
                        item.market_data,
                    ]
                )
                for item in observations
            ]
        )
        confidence = average([item.confidence_score for item in observations])
        score = average([coverage, consistency, visibility, completeness, confidence])
        return AggregationResult(
            score=score,
            coverage=clamp(coverage),
            consistency=clamp(consistency),
            visibility=clamp(visibility),
            completeness=clamp(completeness),
            confidence=clamp(confidence),
            conflicts=float(conflicts),
        )
