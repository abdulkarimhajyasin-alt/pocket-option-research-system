"""Analytics for architecture audit reports."""

from __future__ import annotations

from typing import Any

from app.architecture_audit.models import ProductionResearchCertification


class ArchitectureAuditAnalytics:
    """Build structured architecture audit analytics."""

    def summarize(
        self,
        certification: ProductionResearchCertification,
        architecture: dict[str, Any],
        consistency: dict[str, Any],
        dependency: dict[str, Any],
        performance: dict[str, Any],
        safety: dict[str, Any],
        diagnostics: tuple[Any, ...],
        recommendations: tuple[Any, ...],
    ) -> dict[str, Any]:
        return {
            "score_distribution": {
                "architecture": certification.architecture_score,
                "consistency": certification.consistency_score,
                "dependency": certification.dependency_score,
                "performance": certification.performance_score,
                "safety": certification.safety_score,
            },
            "architecture": architecture,
            "consistency": consistency,
            "dependency": dependency,
            "performance": performance,
            "safety": safety,
            "diagnostics": {item.name: 1 for item in diagnostics},
            "recommendations": {item.title: 1 for item in recommendations},
            "certification": {
                certification.certification_state: certification.overall_score,
            },
            "architecture_audit_only": True,
        }
