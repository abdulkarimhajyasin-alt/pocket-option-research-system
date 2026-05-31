"""Analytics for passive broker observation readiness."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.broker_readiness.models import BrokerReadinessResult


class BrokerReadinessAnalytics:
    """Generate readiness and capability distributions."""

    def summarize(self, result: BrokerReadinessResult) -> dict[str, Any]:
        diagnostics = Counter(item.severity for item in result.diagnostics)
        recommendations = Counter(item.title for item in result.recommendations)
        restrictions = Counter(item.status_ar for item in result.restrictions.checks)
        return {
            "summary": {
                "readiness_score": result.readiness.score,
                "readiness_state": result.readiness.state,
                "capability_score": result.capability.score,
                "safety_score": result.readiness.safety_readiness,
                "validation_score": result.validation.score,
                "warning_count": len(result.diagnostics),
                "failure_count": sum(
                    1 for item in result.restrictions.checks if item.status == "FAIL"
                ),
                "recommendation_count": len(result.recommendations),
                "coverage_level": result.assessment.observation_capability,
                "research_only": True,
                "observation_only": True,
            },
            "readiness_distribution": {
                result.readiness.state: result.readiness.score,
                "المعمارية": result.readiness.architecture_readiness,
                "المراقبة": result.readiness.observation_readiness,
                "البيانات": result.readiness.data_readiness,
            },
            "capability_distribution": result.capability.to_dict(),
            "validation_distribution": result.validation.to_dict(),
            "safety_distribution": {
                "السلامة": result.readiness.safety_readiness,
                "القيود": result.readiness.restriction_compliance,
            },
            "restriction_distribution": dict(restrictions),
            "diagnostics_distribution": dict(diagnostics),
            "recommendation_distribution": dict(recommendations),
            "readiness_timeline": {
                result.timestamp.strftime("%H:%M"): result.readiness.score
            },
            "capability_timeline": {
                result.timestamp.strftime("%H:%M"): result.capability.score
            },
            "safety_timeline": {
                result.timestamp.strftime("%H:%M"): result.readiness.safety_readiness
            },
            "latest": result.to_dict(),
        }
