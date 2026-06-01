"""Control matrix engine."""

from __future__ import annotations

from typing import Any

from app.governance_traceability.schemas import TRACEABILITY_ONLY_FLAGS


class GovernanceControlMatrixEngine:
    """Build a control matrix linked to owners and evidence."""

    def build(self, control_mappings: dict[str, Any]) -> dict[str, Any]:
        rows = []
        for item in control_mappings.get("items", []):
            rows.append(
                {
                    "control": item.get("target_control", ""),
                    "category": item.get("mapping_type", "control"),
                    "owner": item.get("owner", ""),
                    "evidence": item.get("evidence_required", []),
                    "review_board": "Governance Review Board",
                    "readiness_gate": "Governance gate required",
                    "covered": item.get("strength") != "مفقود",
                    **TRACEABILITY_ONLY_FLAGS,
                }
            )
        return {"items": rows, "uncovered_controls": [], **TRACEABILITY_ONLY_FLAGS}
