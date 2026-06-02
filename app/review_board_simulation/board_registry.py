"""Review board registry for local simulation."""

from __future__ import annotations

from typing import Any

from app.review_board_simulation.models import (
    ReviewBoard,
    ReviewBoardCriterion,
    safety_notes,
)
from app.review_board_simulation.schemas import SIMULATION_ONLY_FLAGS


class ReviewBoardRegistry:
    """Define review boards, criteria, and safety expectations."""

    BOARDS = (
        (
            "architecture",
            "Architecture Review Board",
            ("production_system_design", "trading_architecture_program"),
            ("Architecture separation", "Design boundaries", "Future extensibility"),
        ),
        (
            "risk",
            "Risk Review Board",
            ("trading_requirements", "control_assurance"),
            ("Risk controls", "Limits design", "Blocker handling"),
        ),
        (
            "compliance",
            "Compliance Review Board",
            ("operational_governance", "governance_traceability"),
            ("Policy mapping", "Evidence traceability", "Review records"),
        ),
        (
            "operations",
            "Operations Review Board",
            ("operational_governance", "production_system_design"),
            ("Runbook design", "Incident handling", "Monitoring expectations"),
        ),
        (
            "release",
            "Release Review Board",
            ("control_assurance", "trading_architecture_program"),
            ("Gate maturity", "Release criteria", "Readiness evidence"),
        ),
        (
            "incident",
            "Incident Review Board",
            ("operational_governance", "governance_traceability"),
            ("Incident escalation", "Post-incident evidence", "Human review"),
        ),
    )

    def build(self) -> dict[str, Any]:
        boards = []
        for index, (board_id, name, sources, responsibilities) in enumerate(self.BOARDS, start=1):
            criteria = [
                ReviewBoardCriterion(
                    criterion_id=f"RBC-{index}-{item_index}",
                    name=responsibility,
                    evidence_expectations=[
                        "Local JSON source artifact",
                        "Traceable review rationale",
                        "Explicit simulation-only safety note",
                    ],
                    required_sources=list(sources),
                    weight=1.0,
                ).to_dict()
                for item_index, responsibility in enumerate(responsibilities, start=1)
            ]
            boards.append(
                ReviewBoard(
                    board_id=board_id,
                    board_name=name,
                    responsibilities=list(responsibilities),
                    criteria=criteria,
                    forbidden_approvals=[
                        "Any real trading approval is forbidden.",
                        "Any execution readiness approval is forbidden.",
                        "Any broker or account readiness approval is forbidden.",
                    ],
                    safety_notes=safety_notes(),
                ).to_dict()
            )
        return {"boards": boards, **SIMULATION_ONLY_FLAGS}
