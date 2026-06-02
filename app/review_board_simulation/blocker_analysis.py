"""Blocker analysis for review board simulation."""

from __future__ import annotations

from typing import Any

from app.review_board_simulation.models import BlockerFinding
from app.review_board_simulation.schemas import SIMULATION_ONLY_FLAGS


class ReviewBlockerAnalysisEngine:
    """Identify board-level and gate-level blockers."""

    def analyze(
        self,
        board_results: dict[str, Any],
        gate_results: dict[str, Any],
    ) -> dict[str, Any]:
        items = []
        for board in board_results.get("items", []):
            for blocker in board.get("blockers", []):
                items.append(blocker)
        for index, gate in enumerate(gate_results.get("items", []), start=1):
            for blocker in gate.get("blockers", []):
                items.append(
                    BlockerFinding(
                        blocker_id=f"GATE-BLK-{index:02d}",
                        scope=str(gate.get("gate_name")),
                        severity="مرتفع",
                        description=str(blocker),
                        remediation="Complete simulated board coverage and evidence review.",
                    ).to_dict()
                )
        severity_counts: dict[str, int] = {}
        for item in items:
            severity = str(item.get("severity", "متوسط"))
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return {"items": items, "severity_counts": severity_counts, **SIMULATION_ONLY_FLAGS}
