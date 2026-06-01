"""Control quality assurance engine."""

from __future__ import annotations

from typing import Any

from app.control_assurance.models import ControlAssuranceResult, assurance_item


class ControlAssuranceEngine:
    """Assess governance control quality."""

    AREAS = [
        "control clarity",
        "owner assignment",
        "evidence requirement",
        "verification method",
        "review board linkage",
        "readiness gate linkage",
        "safety notes",
        "implementation boundary clarity",
    ]

    def assess(self, sources: dict[str, Any]) -> dict[str, Any]:
        source_bonus = (
            5
            if sources.get("sources", {}).get("governance_traceability", {}).get("available")
            else 0
        )
        items = [
            assurance_item(
                index,
                area,
                "control_quality",
                82 + source_bonus if index <= 6 else 76 + source_bonus,
                "Governance Review Board",
                ["design evidence", "review evidence", "audit evidence"],
            )
            for index, area in enumerate(self.AREAS, 1)
        ]
        return ControlAssuranceResult(items=items).to_dict()
