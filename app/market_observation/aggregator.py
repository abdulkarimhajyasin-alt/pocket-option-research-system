"""Aggregate canonical market observation records."""

from __future__ import annotations

from collections import Counter

from app.market_observation.models import MarketObservationAggregate
from app.market_observation.models import MarketObservationRecord
from app.market_observation.models import MarketObservationValidation
from app.market_observation.scoring import average
from app.market_observation.scoring import state_from_score


class MarketObservationAggregator:
    """Create the canonical market observation source from passive records."""

    def aggregate(
        self,
        observations: tuple[MarketObservationRecord, ...],
        validation: MarketObservationValidation,
    ) -> MarketObservationAggregate:
        coverage = validation.completeness
        quality = average([item.quality_score for item in observations])
        confidence = average([item.confidence_score for item in observations])
        visibility = average([item.visibility_score for item in observations])
        freshness = average([item.freshness_score for item in observations])
        consistency = validation.consistency
        score = average([coverage, quality, confidence, visibility, freshness, consistency])
        state, explanation = state_from_score(score)
        sources = Counter(item.source_type for item in observations)
        return MarketObservationAggregate(
            score=score,
            state=state,
            explanation=explanation,
            coverage_score=coverage,
            quality_score=quality,
            confidence_score=confidence,
            visibility_score=visibility,
            freshness_score=freshness,
            consistency_score=consistency,
            asset_count=max((item.asset_count for item in observations), default=0.0),
            payout_count=max((item.payout_count for item in observations), default=0.0),
            session_count=max((item.session_count for item in observations), default=0.0),
            symbol_count=max((item.symbol_count for item in observations), default=0.0),
            source_distribution=dict(sources),
        )
