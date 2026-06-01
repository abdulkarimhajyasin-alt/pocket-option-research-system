"""Control assurance scoring engine."""

from __future__ import annotations

from typing import Any

from app.control_assurance.models import AssuranceScorecard
from app.control_assurance.schemas import ASSURANCE_ONLY_FLAGS


class ControlAssuranceScoringEngine:
    """Calculate deterministic assurance scores."""

    def build(self, payloads: dict[str, Any]) -> dict[str, Any]:
        control = self._average(payloads["control_quality"].get("items", []))
        evidence = self._average(payloads["evidence_sufficiency"].get("items", []))
        owner = self._average(payloads["owner_clarity"].get("items", []))
        policy = self._average(payloads["policy_completeness"].get("items", []))
        gate = self._average(payloads["gate_maturity"].get("items", []))
        audit = round((control + evidence + owner + policy + gate) / 5, 2)
        review = round((audit + owner + evidence) / 3, 2)
        overall = round((control + evidence + owner + policy + gate + audit + review) / 7, 2)
        payload = AssuranceScorecard(
            control_quality_score=control,
            evidence_sufficiency_score=evidence,
            owner_clarity_score=owner,
            policy_completeness_score=policy,
            gate_maturity_score=gate,
            audit_readiness_score=audit,
            governance_review_readiness_score=review,
            overall_assurance_score=overall,
            score_status=self._status(overall),
        ).to_dict()
        payload.update(ASSURANCE_ONLY_FLAGS)
        return payload

    def _average(self, items: list[dict[str, Any]]) -> float:
        if not items:
            return 0.0
        return round(sum(float(item.get("score", 0)) for item in items) / len(items), 2)

    def _status(self, score: float) -> str:
        if score >= 90:
            return "ممتاز"
        if score >= 80:
            return "جيد"
        if score >= 70:
            return "مقبول"
        if score >= 50:
            return "يحتاج تحسين"
        return "غير جاهز"
