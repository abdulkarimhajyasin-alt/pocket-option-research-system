"""Analytics for unified observation intelligence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.observation_intelligence.models import ObservationIntelligenceResult


class ObservationIntelligenceAnalytics:
    """Generate distributions for unified observation intelligence."""

    def summarize(self, result: ObservationIntelligenceResult) -> dict[str, Any]:
        sources = Counter(item.source_type for item in result.observations)
        diagnostics = Counter(item.severity for item in result.diagnostics)
        recommendations = Counter(item.title for item in result.recommendations)
        source_quality = {
            item.source_name: item.quality_score for item in result.observations
        }
        conflicts = {
            "تضارب": result.aggregation.conflicts,
            "اتساق": result.aggregation.consistency,
        }
        return {
            "summary": {
                "observation_count": len(result.observations),
                "quality_score": result.quality.score,
                "confidence_score": result.confidence.score,
                "consistency_score": result.aggregation.consistency,
                "coverage_score": result.aggregation.coverage,
                "readiness_score": result.intelligence.observation_readiness,
                "intelligence_score": result.intelligence.score,
                "intelligence_state": result.intelligence.state,
                "warning_count": len(result.diagnostics),
                "recommendation_count": len(result.recommendations),
                "research_only": True,
                "observation_only": True,
            },
            "source_distribution": dict(sources),
            "quality_distribution": result.quality.to_dict(),
            "confidence_distribution": result.confidence.to_dict(),
            "consistency_distribution": {
                "الاتساق": result.aggregation.consistency,
                "التحقق": result.validation.consistency,
            },
            "coverage_distribution": {
                "التغطية": result.aggregation.coverage,
                "الاكتمال": result.aggregation.completeness,
            },
            "readiness_distribution": result.intelligence.to_dict(),
            "conflict_distribution": conflicts,
            "source_quality": source_quality,
            "diagnostics_distribution": dict(diagnostics),
            "recommendation_distribution": dict(recommendations),
            "latest": result.to_dict(),
        }
