"""Allowed capability validation."""

from __future__ import annotations

from typing import Any

from app.integration_safety.models import ALLOWED_CAPABILITIES


class IntegrationPermissionEngine:
    """Validate that only explicitly allowed local capabilities are present."""

    def evaluate(self, declared_capabilities: tuple[str, ...]) -> dict[str, Any]:
        unknown = [
            capability
            for capability in declared_capabilities
            if capability not in ALLOWED_CAPABILITIES
        ]
        score = 100.0 if not unknown else max(0.0, 100.0 - len(unknown) * 20.0)
        return {
            "allowed_capabilities": list(ALLOWED_CAPABILITIES),
            "declared_capabilities": list(declared_capabilities),
            "unknown_capabilities": unknown,
            "permission_score": round(score, 2),
            "safety_boundary_only": True,
        }
