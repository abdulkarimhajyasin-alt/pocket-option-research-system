"""Analytics for the external observation sandbox."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.external_observation.models import ExternalObservationResult


class ExternalObservationAnalytics:
    """Generate source, health, validation, monitoring, and isolation analytics."""

    def summarize(self, result: ExternalObservationResult) -> dict[str, Any]:
        source_types = Counter(item.source_type for item in result.sources)
        diagnostics = Counter(item.severity for item in result.diagnostics)
        recommendations = Counter(item.title for item in result.recommendations)
        return {
            "summary": {
                "source_count": len(result.sources),
                "sandbox_score": result.sandbox.score,
                "sandbox_state": result.sandbox.state,
                "health_score": result.health.score,
                "validation_score": result.validation.score,
                "monitoring_score": result.monitoring.score,
                "isolation_score": result.isolation.score,
                "warning_count": len(result.diagnostics),
                "recommendation_count": len(result.recommendations),
                "research_only": True,
                "observation_only": True,
            },
            "source_distribution": dict(source_types),
            "health_distribution": result.health.to_dict(),
            "validation_distribution": result.validation.to_dict(),
            "monitoring_distribution": result.monitoring.to_dict(),
            "isolation_distribution": {
                "لا اتصال وسيط": 100.0
                if result.isolation.no_broker_connectivity
                else 0.0,
                "لا وصول حساب": 100.0 if result.isolation.no_account_access else 0.0,
                "لا مسارات تنفيذ": 100.0
                if result.isolation.no_execution_paths
                else 0.0,
                "لا مصادقة": 100.0
                if result.isolation.no_authentication_flows
                else 0.0,
                "لا أوامر": 100.0 if result.isolation.no_order_apis else 0.0,
            },
            "source_quality": {
                item.source_name: 100.0
                if item.validation_status == "ناجح"
                else 50.0
                for item in result.sources
            },
            "source_stability": {
                item.source_name: 100.0
                if item.observation_status == "نشط"
                else 50.0
                for item in result.sources
            },
            "source_coverage": {
                item.source_name: 100.0
                if item.visibility_scope
                else 0.0
                for item in result.sources
            },
            "diagnostics_distribution": dict(diagnostics),
            "recommendation_distribution": dict(recommendations),
            "latest": result.to_dict(),
        }
