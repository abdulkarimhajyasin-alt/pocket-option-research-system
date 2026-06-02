"""Findings builder for review board simulation."""

from __future__ import annotations

from typing import Any

from app.review_board_simulation.schemas import SIMULATION_ONLY_FLAGS


class ReviewSimulationFindingsBuilder:
    """Build dry-run findings from decisions, gates, and blockers."""

    def build(
        self,
        board_results: dict[str, Any],
        gate_results: dict[str, Any],
        blocker_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        items = []
        for board in board_results.get("items", []):
            if board.get("readiness_score", 0) < 90:
                items.append(
                    {
                        "finding_id": f"FIND-{len(items) + 1:02d}",
                        "scope": board.get("board_name"),
                        "finding_type": "board-readiness",
                        "message": "Board is not fully ready for a clean simulated pass.",
                        "required_action": "Complete evidence review and human governance review.",
                    }
                )
        for gate in gate_results.get("items", []):
            if gate.get("required_human_review"):
                items.append(
                    {
                        "finding_id": f"FIND-{len(items) + 1:02d}",
                        "scope": gate.get("gate_name"),
                        "finding_type": "gate-human-review",
                        "message": "Gate requires human review in this dry run.",
                        "required_action": "Resolve conditions before future program expansion.",
                    }
                )
        return {
            "items": items,
            "blocker_count": len(blocker_analysis.get("items", [])),
            **SIMULATION_ONLY_FLAGS,
        }
