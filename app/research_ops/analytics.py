"""Analytics for research operations."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.research_ops.models import ResearchOperationsResult


class ResearchOperationsAnalytics:
    """Generate executive operations analytics."""

    def summarize(self, result: ResearchOperationsResult) -> dict[str, Any]:
        alerts = [item.severity for item in result.alerts]
        recs = [item.title for item in result.recommendations]
        risks = result.risk_assessment.risks
        timestamp = result.timestamp.strftime("%H:%M")
        return {
            "summary": {
                "health_score": result.executive_summary.research_health.score,
                "health_classification": (
                    result.executive_summary.research_health.classification
                ),
                "readiness_score": result.strategy_status.readiness_score,
                "opportunity_count": result.opportunity_status.opportunity_count,
                "alert_count": len(result.alerts),
                "risk_count": len(risks),
                "recommendation_count": len(result.recommendations),
                "best_opportunity": result.opportunity_status.top_opportunity,
                "last_update": result.timestamp.isoformat(),
                "research_only": True,
            },
            "health_trends": {timestamp: result.executive_summary.research_health.score},
            "readiness_trends": {timestamp: result.strategy_status.readiness_score},
            "confluence_trends": {
                timestamp: result.opportunity_status.strongest_confluence
            },
            "performance_trends": {timestamp: result.strategy_status.confidence_stability},
            "opportunity_quality_trends": {
                timestamp: result.strategy_status.research_quality
            },
            "alert_distribution": dict(Counter(alerts)),
            "recommendation_distribution": dict(Counter(recs)),
            "risk_distribution": dict(Counter(risks)),
            "quality_trends": {timestamp: result.strategy_status.lifecycle_quality},
            "stability_trends": {timestamp: result.strategy_status.confidence_stability},
            "latest": result.to_dict(),
        }
