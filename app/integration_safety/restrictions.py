"""Forbidden capability validation."""

from __future__ import annotations

from typing import Any

from app.integration_safety.models import FORBIDDEN_CAPABILITIES


class IntegrationRestrictionEngine:
    """Validate that forbidden capabilities remain absent."""

    def evaluate(self, detected_capabilities: tuple[str, ...]) -> dict[str, Any]:
        violations = [
            capability
            for capability in detected_capabilities
            if capability in FORBIDDEN_CAPABILITIES
        ]
        score = 100.0 if not violations else max(0.0, 100.0 - len(violations) * 25.0)
        return {
            "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
            "detected_capabilities": list(detected_capabilities),
            "violations": violations,
            "restriction_score": round(score, 2),
            "safety_boundary_only": True,
        }
