"""Governance traceability mapping engine."""

from __future__ import annotations

from typing import Any

from app.governance_traceability.models import ControlMapping, mapping_item


class GovernanceTraceabilityMappingEngine:
    """Build production-to-governance control mappings."""

    DESIGN_AREAS = [
        "topology",
        "service boundaries",
        "runtime architecture",
        "environment strategy",
        "configuration strategy",
        "secrets strategy",
        "database strategy",
        "event queue strategy",
        "logging strategy",
        "monitoring strategy",
        "alerting strategy",
        "incident response",
        "backup recovery",
        "release rollback",
        "readiness gates",
    ]

    CONTROL_ROTATION = [
        "authority model",
        "approval workflows",
        "change management",
        "release governance",
        "incident escalation",
        "emergency stop governance",
        "audit controls",
        "operator responsibility",
        "review boards",
        "decision matrix",
        "control evidence",
        "policy registry",
    ]

    def build(self, sources: dict[str, Any]) -> dict[str, Any]:
        items = [
            mapping_item(
                index,
                area,
                self.CONTROL_ROTATION[(index - 1) % len(self.CONTROL_ROTATION)],
                "control",
                "Governance Review Board",
                ["design evidence", "review evidence", "audit evidence"],
                "قوي" if index <= 12 else "متوسط",
            )
            for index, area in enumerate(self.DESIGN_AREAS, 1)
        ]
        payload = ControlMapping(items=items).to_dict()
        payload["source_available"] = sources.get("sources", {})
        return payload
