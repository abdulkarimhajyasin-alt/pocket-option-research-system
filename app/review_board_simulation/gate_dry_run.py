"""Decision gate dry-run engine."""

from __future__ import annotations

from typing import Any

from app.review_board_simulation.models import DecisionGateDryRun
from app.review_board_simulation.schemas import SIMULATION_ONLY_FLAGS


class DecisionGateDryRunEngine:
    """Dry-run decision gates without real approvals."""

    GATES = (
        "Research Platform Frozen",
        "Documentation Complete",
        "Architecture Separation Approved",
        "Risk Architecture Approved",
        "Governance Approved",
        "External Integration Review Approved",
        "Future Program Approval",
        "Requirements Approved",
        "Production Design Review",
        "Governance Review",
        "Control Assurance Review",
    )

    REQUIRED_BOARD_COVERAGE = {
        "Research Platform Frozen": ("Release Review Board",),
        "Documentation Complete": ("Operations Review Board",),
        "Architecture Separation Approved": ("Architecture Review Board",),
        "Risk Architecture Approved": ("Risk Review Board",),
        "Governance Approved": ("Compliance Review Board",),
        "External Integration Review Approved": ("Incident Review Board",),
        "Future Program Approval": ("Release Review Board",),
        "Requirements Approved": ("Risk Review Board",),
        "Production Design Review": ("Architecture Review Board",),
        "Governance Review": ("Compliance Review Board",),
        "Control Assurance Review": ("Operations Review Board",),
    }

    def run(self, board_results: dict[str, Any], evidence_review: dict[str, Any]) -> dict[str, Any]:
        boards = {item.get("board_name"): item for item in board_results.get("items", [])}
        evidence_score = self._average(
            [float(item.get("linkage_score", 0.0)) for item in evidence_review.get("items", [])]
        )
        items = []
        for gate in self.GATES:
            required_boards = self.REQUIRED_BOARD_COVERAGE[gate]
            board_scores = [
                float(boards.get(board, {}).get("readiness_score", 0.0))
                for board in required_boards
            ]
            missing_boards = [board for board in required_boards if board not in boards]
            score = round((self._average(board_scores) * 0.65) + (evidence_score * 0.35), 2)
            blockers = [f"Missing review board coverage: {board}" for board in missing_boards]
            conditions = []
            if score < 90:
                conditions.append("Gate remains a dry-run finding pending human review.")
            state = self._state(score, bool(blockers))
            items.append(
                DecisionGateDryRun(
                    gate_name=gate,
                    simulated_state=state,
                    readiness_score=score,
                    evidence_reviewed=[
                        str(item.get("source_group")) for item in evidence_review.get("items", [])
                    ],
                    blockers=blockers,
                    conditions=conditions,
                    required_human_review=state != "Simulated Pass",
                    forbidden_real_world_use=True,
                ).to_dict()
            )
        return {"items": items, **SIMULATION_ONLY_FLAGS}

    def _state(self, score: float, blocked: bool) -> str:
        if blocked:
            return "Simulated Blocked"
        if score >= 90:
            return "Simulated Pass"
        if score >= 70:
            return "Simulated Conditional Pass"
        if score >= 45:
            return "Requires Human Review"
        return "Simulated Not Ready"

    def _average(self, values: list[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)
