"""Readiness summary builder for review board simulation."""

from __future__ import annotations

from typing import Any

from app.review_board_simulation.models import ReviewSimulationSummary
from app.review_board_simulation.schemas import SIMULATION_ONLY_FLAGS


class ReviewSimulationReadinessBuilder:
    """Build aggregate readiness summary."""

    def build(
        self,
        decision_scores: dict[str, Any],
        board_results: dict[str, Any],
        gate_results: dict[str, Any],
        blocker_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        decisions = [
            decision
            for board in board_results.get("items", [])
            for decision in board.get("simulated_decisions", [])
        ]
        gates = gate_results.get("items", [])
        human_reviews = sum(1 for item in decisions + gates if item.get("required_human_review"))
        conditions = sum(len(item.get("conditions", [])) for item in decisions + gates)
        score = float(decision_scores.get("overall_review_readiness_score", 0.0))
        status = decision_scores.get("score_status", "غير جاهز")
        summary = ReviewSimulationSummary(
            simulation_status=str(status),
            overall_review_readiness_score=score,
            simulated_decision_count=len(decisions),
            blocker_count=len(blocker_analysis.get("items", [])),
            condition_count=conditions,
            required_human_review_count=human_reviews,
        ).to_dict()
        return {**summary, **SIMULATION_ONLY_FLAGS}
