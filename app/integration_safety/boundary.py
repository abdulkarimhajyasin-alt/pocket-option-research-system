"""Boundary status evaluation."""

from __future__ import annotations

from typing import Any

from app.integration_safety.models import (
    BOUNDARY_CONDITIONALLY_PROTECTED,
    BOUNDARY_FULLY_PROTECTED,
    BOUNDARY_NEEDS_REVIEW,
    BOUNDARY_UNSAFE,
)


class IntegrationBoundaryEngine:
    """Evaluate architecture safety boundary state."""

    def evaluate(
        self,
        permissions: dict[str, Any],
        restrictions: dict[str, Any],
        compliance: dict[str, Any],
    ) -> dict[str, Any]:
        permission_score = float(permissions.get("permission_score", 0.0))
        restriction_score = float(restrictions.get("restriction_score", 0.0))
        compliance_score = float(compliance.get("compliance_score", 0.0))
        violations = restrictions.get("violations", [])
        safety_score = round(
            (permission_score + restriction_score + compliance_score) / 3.0,
            2,
        )
        if violations:
            status = BOUNDARY_UNSAFE
        elif safety_score >= 95:
            status = BOUNDARY_FULLY_PROTECTED
        elif safety_score >= 85:
            status = BOUNDARY_CONDITIONALLY_PROTECTED
        elif safety_score >= 70:
            status = BOUNDARY_NEEDS_REVIEW
        else:
            status = BOUNDARY_UNSAFE
        risks = []
        if permission_score < 100:
            risks.append("ambiguous capability")
        if restriction_score < 100:
            risks.append("forbidden capability risk")
        if compliance_score < 100:
            risks.append("missing safety metadata")
        return {
            "boundary_status": status,
            "safety_score": safety_score,
            "permission_score": permission_score,
            "restriction_score": restriction_score,
            "compliance_score": compliance_score,
            "boundary_risks": risks,
            "safety_boundary_only": True,
        }
