"""Audit record generation for integration safety."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class IntegrationSafetyAudit:
    """Generate an audit record for the safety boundary."""

    def build(
        self,
        allowed: tuple[str, ...],
        forbidden: tuple[str, ...],
        restrictions: dict[str, Any],
        diagnostics: tuple[Any, ...],
        recommendations: tuple[Any, ...],
        metadata: dict[str, bool],
    ) -> dict[str, Any]:
        return {
            "audit_id": f"integration_safety_audit_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.now(UTC).isoformat(),
            "allowed_capabilities": list(allowed),
            "forbidden_capabilities": list(forbidden),
            "detected_violations": restrictions.get("violations", []),
            "warnings": [item.to_dict() for item in diagnostics],
            "recommendations": [item.to_dict() for item in recommendations],
            "safety_metadata": metadata,
            "safety_boundary_only": True,
            "research_only": True,
        }
