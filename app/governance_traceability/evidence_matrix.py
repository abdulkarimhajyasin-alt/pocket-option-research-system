"""Evidence matrix builder."""

from __future__ import annotations

from typing import Any

from app.governance_traceability.models import EvidenceMapping, mapping_item


class EvidenceMatrixBuilder:
    """Map controls to evidence types."""

    EVIDENCE_TYPES = [
        "design evidence",
        "review evidence",
        "approval evidence",
        "test evidence",
        "audit evidence",
        "incident evidence",
        "rollback evidence",
        "monitoring evidence",
    ]

    def build(self, control_mappings: dict[str, Any]) -> dict[str, Any]:
        controls = control_mappings.get("items", [])
        items = [
            mapping_item(
                index,
                str(control.get("target_control", "")),
                self.EVIDENCE_TYPES[(index - 1) % len(self.EVIDENCE_TYPES)],
                "evidence",
                str(control.get("owner", "Governance Review Board")),
                [self.EVIDENCE_TYPES[(index - 1) % len(self.EVIDENCE_TYPES)]],
            )
            for index, control in enumerate(controls, 1)
        ]
        return EvidenceMapping(items=items).to_dict()
