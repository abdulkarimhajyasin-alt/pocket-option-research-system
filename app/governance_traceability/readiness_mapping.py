"""Readiness gate traceability builder."""

from __future__ import annotations

from app.governance_traceability.models import ReadinessGateMapping, mapping_item


class ReadinessMappingBuilder:
    """Map production readiness gates to governance readiness gates."""

    def build(self) -> dict[str, object]:
        gates = [
            "requirements approved",
            "architecture approved",
            "risk design approved",
            "monitoring design approved",
            "incident response approved",
            "compliance review complete",
            "staging validation complete",
            "rollback tested",
            "operator training complete",
        ]
        items = [
            mapping_item(
                index,
                gate,
                "governance readiness gate",
                "readiness",
                "Approval Board",
                ["approval evidence", "review evidence"],
            )
            for index, gate in enumerate(gates, 1)
        ]
        return ReadinessGateMapping(items=items).to_dict()
