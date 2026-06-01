"""Governance review readiness engine."""

from __future__ import annotations

from typing import Any

from app.control_assurance.models import GovernanceReviewReadiness
from app.control_assurance.schemas import ASSURANCE_ONLY_FLAGS


class GovernanceReviewReadinessEngine:
    """Classify governance review readiness."""

    def assess(self, payloads: dict[str, Any], scorecard: dict[str, Any]) -> dict[str, Any]:
        weak_control_count = sum(
            1
            for item in payloads["control_quality"].get("items", [])
            if str(item.get("status")) in {"ضعيف", "غير جاهز"}
        )
        missing_evidence_count = sum(
            len(item.get("missing_evidence", []))
            for item in payloads["evidence_sufficiency"].get("items", [])
        )
        missing_owner_count = sum(
            1 for item in payloads["owner_clarity"].get("items", []) if not item.get("owner")
        )
        blocker_count = weak_control_count + missing_evidence_count + missing_owner_count
        score = float(scorecard.get("governance_review_readiness_score", 0))
        state = (
            "Ready For Governance Review"
            if blocker_count == 0 and score >= 80
            else "Review Blocked"
        )
        payload = GovernanceReviewReadiness(
            review_readiness_state=state,
            blocker_count=blocker_count,
            missing_evidence_count=missing_evidence_count,
            weak_control_count=weak_control_count,
            missing_owner_count=missing_owner_count,
        ).to_dict()
        payload.update(ASSURANCE_ONLY_FLAGS)
        return payload
