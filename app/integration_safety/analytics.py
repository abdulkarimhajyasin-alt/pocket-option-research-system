"""Analytics for integration safety boundary."""

from __future__ import annotations

from typing import Any

from app.integration_safety.models import IntegrationSafetyPolicy


class IntegrationSafetyAnalytics:
    """Build structured analytics for safety reports and dashboard."""

    def summarize(
        self,
        policy: IntegrationSafetyPolicy,
        boundary: dict[str, Any],
        permissions: dict[str, Any],
        restrictions: dict[str, Any],
        compliance: dict[str, Any],
        audit: dict[str, Any],
        diagnostics: tuple[Any, ...],
        recommendations: tuple[Any, ...],
    ) -> dict[str, Any]:
        return {
            "safety_distribution": {
                "safety_score": policy.safety_score,
                "compliance_score": policy.compliance_score,
                "restriction_score": restrictions.get("restriction_score", 0.0),
                "permission_score": permissions.get("permission_score", 0.0),
            },
            "compliance_distribution": compliance,
            "restriction_distribution": {
                "allowed": len(policy.allowed_capabilities),
                "forbidden": len(policy.forbidden_capabilities),
                "violations": len(restrictions.get("violations", [])),
            },
            "allowed_capabilities": {
                value: 1 for value in policy.allowed_capabilities
            },
            "forbidden_capabilities": {
                value: 1 for value in policy.forbidden_capabilities
            },
            "warnings": {item.name: 1 for item in diagnostics},
            "recommendations": {item.title: 1 for item in recommendations},
            "boundary_status": {policy.boundary_status: policy.safety_score},
            "audit_record": {
                "allowed": len(audit.get("allowed_capabilities", [])),
                "forbidden": len(audit.get("forbidden_capabilities", [])),
                "violations": len(audit.get("detected_violations", [])),
                "warnings": len(audit.get("warnings", [])),
            },
            "safety_boundary_only": True,
        }
