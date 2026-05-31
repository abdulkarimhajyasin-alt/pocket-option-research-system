"""Analytics for read-only browser observation artifacts."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.browser_observation.models import BrowserObservationResult


class BrowserObservationAnalytics:
    """Generate artifact, readiness, visibility, validation, and monitoring analytics."""

    def summarize(self, result: BrowserObservationResult) -> dict[str, Any]:
        artifact_types = Counter(item.artifact_type for item in result.artifacts)
        diagnostics = Counter(item.severity for item in result.diagnostics)
        recommendations = Counter(item.title for item in result.recommendations)
        return {
            "summary": {
                "artifact_count": len(result.artifacts),
                "adapter_score": result.adapter.score,
                "adapter_state": result.adapter.state,
                "safety_score": result.safety.score,
                "validation_score": result.validation.score,
                "visibility_score": result.visibility.score,
                "monitoring_score": result.monitoring.score,
                "warning_count": len(result.diagnostics),
                "recommendation_count": len(result.recommendations),
                "research_only": True,
                "observation_only": True,
                "read_only": True,
            },
            "artifact_distribution": dict(artifact_types),
            "readiness_distribution": result.adapter.to_dict(),
            "visibility_distribution": result.visibility.to_dict(),
            "validation_distribution": result.validation.to_dict(),
            "monitoring_distribution": result.monitoring.to_dict(),
            "safety_distribution": {
                "لا تسجيل دخول": 100.0 if result.safety.no_login else 0.0,
                "لا مصادقة": 100.0 if result.safety.no_authentication else 0.0,
                "لا تحكم متصفح": 100.0
                if result.safety.no_browser_control
                else 0.0,
                "لا تنفيذ": 100.0 if result.safety.no_execution else 0.0,
                "لا أوامر": 100.0 if result.safety.no_order_apis else 0.0,
                "لا وصول حساب": 100.0 if result.safety.no_account_access else 0.0,
                "لا أتمتة": 100.0 if result.safety.no_automation else 0.0,
            },
            "artifact_quality": {
                item.artifact_id: 100.0
                if item.validation_status == "ناجح"
                else 50.0
                for item in result.artifacts
            },
            "artifact_stability": {
                item.artifact_id: 100.0
                if item.monitoring_status == "مستقر"
                else 50.0
                for item in result.artifacts
            },
            "diagnostics_distribution": dict(diagnostics),
            "recommendation_distribution": dict(recommendations),
            "latest": result.to_dict(),
        }
