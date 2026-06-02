"""Baseline readiness scoring."""

from __future__ import annotations

from typing import Any

from app.release_baseline.models import BaselineScorecard
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS


class BaselineScoringEngine:
    """Calculate release baseline readiness scores."""

    def build(
        self,
        inventory: dict[str, Any],
        classifications: dict[str, Any],
        reconciliation: dict[str, Any],
        checklist: dict[str, Any],
        evidence: dict[str, Any],
        ignore_review: dict[str, Any],
    ) -> dict[str, Any]:
        total = max(len(inventory.get("items", [])), 1)
        classified = len(classifications.get("items", []))
        manual = sum(
            1
            for item in classifications.get("items", [])
            if item.get("requires_human_review")
        )
        baseline_clarity = round(min(100.0, (classified / total) * 100.0), 2)
        commit_readiness = round(max(0.0, 100.0 - (manual / max(classified, 1)) * 35.0), 2)
        artifact_score = 100.0 if reconciliation.get("items") else 0.0
        cleanup_score = 100.0 if checklist.get("items") else 0.0
        evidence_score = 100.0 if evidence.get("items") else 60.0
        ignore_score = 95.0 if ignore_review.get("items") else 80.0
        overall = round(
            baseline_clarity * 0.2
            + commit_readiness * 0.25
            + artifact_score * 0.2
            + cleanup_score * 0.15
            + evidence_score * 0.1
            + ignore_score * 0.1,
            2,
        )
        return {
            **BaselineScorecard(
                baseline_clarity_score=baseline_clarity,
                commit_readiness_score=commit_readiness,
                artifact_reconciliation_score=artifact_score,
                manual_cleanup_readiness_score=cleanup_score,
                evidence_selection_score=evidence_score,
                ignore_review_score=ignore_score,
                overall_baseline_readiness_score=overall,
                baseline_state=self._state(overall, manual),
            ).to_dict(),
            **BASELINE_ONLY_FLAGS,
        }

    def _state(self, score: float, manual_count: int) -> str:
        if score < 60:
            return "Not Ready"
        if manual_count > 0:
            return "Needs Manual Review"
        return "Ready For Baseline Commit Review"
