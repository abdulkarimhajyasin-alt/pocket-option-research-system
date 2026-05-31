"""Validation for canonical market observations."""

from __future__ import annotations

from collections import Counter

from app.market_observation.models import MarketObservationRecord
from app.market_observation.models import MarketObservationValidation
from app.market_observation.scoring import average
from app.market_observation.scoring import clamp


class MarketObservationValidationEngine:
    """Validate normalized source structure and safety constraints."""

    expected_sources = 7

    def validate(
        self,
        observations: tuple[MarketObservationRecord, ...],
    ) -> MarketObservationValidation:
        source_counts = Counter(item.source_type for item in observations)
        duplicates = sum(1 for count in source_counts.values() if count > 1)
        completeness = clamp(len(observations) / self.expected_sources * 100.0)
        consistency = clamp(100.0 - duplicates * 25.0)
        integrity = average(
            [
                100.0 if item.observation_id and item.source_type else 0.0
                for item in observations
            ]
        )
        return MarketObservationValidation(
            score=average([completeness, consistency, integrity]),
            source_count=self.expected_sources,
            normalized_count=len(observations),
            completeness=completeness,
            consistency=consistency,
            integrity=integrity,
        )
