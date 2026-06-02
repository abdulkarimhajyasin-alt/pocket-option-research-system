"""Review board simulation engine."""

from __future__ import annotations

from typing import Any

from app.review_board_simulation.models import (
    BlockerFinding,
    ReviewBoardSimulationResult,
    SimulatedDecision,
    safety_notes,
)
from app.review_board_simulation.schemas import SIMULATION_ONLY_FLAGS
from app.review_board_simulation.decision_scoring import ReviewDecisionScoringEngine


class ReviewBoardSimulationEngine:
    """Simulate board reviews from local artifacts only."""

    GATES_BY_BOARD = {
        "Architecture Review Board": (
            "Architecture Separation Approved",
            "Production Design Review",
        ),
        "Risk Review Board": ("Risk Architecture Approved", "Requirements Approved"),
        "Compliance Review Board": ("Governance Approved", "Governance Review"),
        "Operations Review Board": ("Control Assurance Review", "Documentation Complete"),
        "Release Review Board": ("Research Platform Frozen", "Future Program Approval"),
        "Incident Review Board": ("External Integration Review Approved",),
    }

    def __init__(self) -> None:
        self.scoring = ReviewDecisionScoringEngine()

    def simulate(
        self,
        sources: dict[str, Any],
        registry: dict[str, Any],
        evidence_review: dict[str, Any],
    ) -> dict[str, Any]:
        evidence_by_group = {
            item["source_group"]: item for item in evidence_review.get("items", [])
        }
        items = []
        for board in registry.get("boards", []):
            criteria_results = []
            blockers = []
            scores = []
            for criterion in board.get("criteria", []):
                required = criterion.get("required_sources", [])
                available = [
                    group
                    for group in required
                    if sources.get("sources", {}).get(group, {}).get("available")
                ]
                score = round(100.0 * (len(available) / max(len(required), 1)), 2)
                scores.append(score)
                missing = sorted(set(required).difference(available))
                criteria_results.append(
                    {
                        "criterion_id": criterion.get("criterion_id"),
                        "name": criterion.get("name"),
                        "score": score,
                        "available_sources": available,
                        "missing_sources": missing,
                        "status": self.scoring.status(score),
                    }
                )
                for group in missing:
                    blockers.append(
                        BlockerFinding(
                            blocker_id=f"BLK-{board.get('board_id')}-{group}",
                            scope=str(board.get("board_name")),
                            severity="مرتفع",
                            description=f"Missing local evidence for {group}",
                            remediation="Generate or attach the missing local review artifact.",
                        ).to_dict()
                    )
            board_score = round(sum(scores) / len(scores), 2) if scores else 0.0
            decisions = [
                self._decision(board, gate, board_score, evidence_by_group, blockers)
                for gate in self.GATES_BY_BOARD.get(str(board.get("board_name")), ())
            ]
            items.append(
                ReviewBoardSimulationResult(
                    board_name=str(board.get("board_name")),
                    criteria_results=criteria_results,
                    simulated_decisions=decisions,
                    blockers=blockers,
                    readiness_score=board_score,
                    readiness_status=self.scoring.status(board_score),
                ).to_dict()
            )
        return {"items": items, **SIMULATION_ONLY_FLAGS}

    def _decision(
        self,
        board: dict[str, Any],
        gate: str,
        score: float,
        evidence_by_group: dict[str, dict[str, Any]],
        blockers: list[dict[str, Any]],
    ) -> dict[str, Any]:
        state = self._state(score, bool(blockers))
        conditions = []
        if score < 90:
            conditions.append("Complete human review of evidence sufficiency before any expansion.")
        evidence = sorted(evidence_by_group.keys())
        return SimulatedDecision(
            decision_id=f"SIM-{board.get('board_id')}-{gate.lower().replace(' ', '-')}",
            board_name=str(board.get("board_name")),
            gate_name=gate,
            simulated_state=state,
            rationale="Dry-run result based on local JSON evidence coverage only.",
            evidence_reviewed=evidence,
            blockers=[str(item.get("description")) for item in blockers],
            conditions=conditions,
            required_human_review=state != "Simulated Pass",
            safety_notes=safety_notes(),
            forbidden_real_world_use=True,
        ).to_dict()

    def _state(self, score: float, has_blockers: bool) -> str:
        if has_blockers:
            return "Simulated Blocked"
        if score >= 90:
            return "Simulated Pass"
        if score >= 70:
            return "Simulated Conditional Pass"
        if score >= 45:
            return "Requires Human Review"
        return "Simulated Not Ready"
