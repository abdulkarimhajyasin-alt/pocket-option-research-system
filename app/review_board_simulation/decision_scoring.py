"""Scoring engine for review board simulation."""

from __future__ import annotations

from typing import Any

from app.review_board_simulation.models import BoardReadinessScore, GateReadinessScore
from app.review_board_simulation.schemas import SIMULATION_ONLY_FLAGS


class ReviewDecisionScoringEngine:
    """Calculate deterministic 0-100 readiness scores."""

    def build(
        self,
        board_results: dict[str, Any],
        gate_results: dict[str, Any],
        evidence_review: dict[str, Any],
    ) -> dict[str, Any]:
        board_scores = [
            BoardReadinessScore(
                board_name=str(item.get("board_name", "")),
                score=self._float(item.get("readiness_score")),
                status=self.status(self._float(item.get("readiness_score"))),
            ).to_dict()
            for item in board_results.get("items", [])
        ]
        gate_scores = [
            GateReadinessScore(
                gate_name=str(item.get("gate_name", "")),
                score=self._float(item.get("readiness_score")),
                status=self.status(self._float(item.get("readiness_score"))),
            ).to_dict()
            for item in gate_results.get("items", [])
        ]
        evidence_scores = [
            self._float(item.get("linkage_score")) for item in evidence_review.get("items", [])
        ]
        evidence_score = self._average(evidence_scores)
        board_score = self._average([item["score"] for item in board_scores])
        gate_score = self._average([item["score"] for item in gate_scores])
        overall = round((board_score * 0.4) + (gate_score * 0.35) + (evidence_score * 0.25), 2)
        return {
            "board_scores": board_scores,
            "gate_scores": gate_scores,
            "architecture_board_score": self._score_for(board_scores, "Architecture"),
            "risk_board_score": self._score_for(board_scores, "Risk"),
            "compliance_board_score": self._score_for(board_scores, "Compliance"),
            "operations_board_score": self._score_for(board_scores, "Operations"),
            "release_board_score": self._score_for(board_scores, "Release"),
            "incident_board_score": self._score_for(board_scores, "Incident"),
            "evidence_readiness_score": evidence_score,
            "gate_readiness_score": gate_score,
            "overall_review_readiness_score": overall,
            "score_status": self.status(overall),
            **SIMULATION_ONLY_FLAGS,
        }

    def status(self, score: float) -> str:
        if score >= 90:
            return "ممتاز"
        if score >= 80:
            return "جيد"
        if score >= 65:
            return "مقبول"
        if score >= 45:
            return "يحتاج تحسين"
        return "غير جاهز"

    def _score_for(self, board_scores: list[dict[str, Any]], name_part: str) -> float:
        for item in board_scores:
            if name_part in str(item.get("board_name", "")):
                return self._float(item.get("score"))
        return 0.0

    def _average(self, values: list[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)

    def _float(self, value: Any) -> float:
        try:
            return round(float(value), 2)
        except (TypeError, ValueError):
            return 0.0
