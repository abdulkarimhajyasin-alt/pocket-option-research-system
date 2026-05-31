"""Analytics for canonical market observation reports and dashboard."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.market_observation.models import MarketObservationResult


class MarketObservationAnalytics:
    """Build deterministic dashboard distributions."""

    def summarize(self, result: MarketObservationResult) -> dict[str, Any]:
        diagnostics = Counter(item.severity for item in result.diagnostics)
        source_quality = {
            item.source_name: item.quality_score for item in result.observations
        }
        source_confidence = {
            item.source_name: item.confidence_score for item in result.observations
        }
        aggregate = result.aggregate
        return {
            "summary": {
                "observation_count": len(result.observations),
                "canonical_score": aggregate.score,
                "canonical_state": aggregate.state,
                "coverage_score": aggregate.coverage_score,
                "quality_score": aggregate.quality_score,
                "confidence_score": aggregate.confidence_score,
                "visibility_score": aggregate.visibility_score,
                "freshness_score": aggregate.freshness_score,
                "consistency_score": aggregate.consistency_score,
                "asset_count": aggregate.asset_count,
                "payout_count": aggregate.payout_count,
                "session_count": aggregate.session_count,
                "symbol_count": aggregate.symbol_count,
                "diagnostic_count": len(result.diagnostics),
                "research_only": True,
                "observation_only": True,
                "canonical_market_observation": True,
            },
            "source_distribution": aggregate.source_distribution,
            "score_distribution": {
                "التغطية": aggregate.coverage_score,
                "الجودة": aggregate.quality_score,
                "الثقة": aggregate.confidence_score,
                "الرؤية": aggregate.visibility_score,
                "الحداثة": aggregate.freshness_score,
                "الاتساق": aggregate.consistency_score,
            },
            "market_distribution": {
                "الأصول": aggregate.asset_count,
                "العوائد": aggregate.payout_count,
                "الجلسات": aggregate.session_count,
                "الرموز": aggregate.symbol_count,
            },
            "source_quality": source_quality,
            "source_confidence": source_confidence,
            "validation": result.validation.to_dict(),
            "diagnostics_distribution": dict(diagnostics),
            "latest": result.to_dict(),
        }
