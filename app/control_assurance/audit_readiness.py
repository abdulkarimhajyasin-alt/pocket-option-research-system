"""Audit readiness assessment."""

from __future__ import annotations

from typing import Any

from app.control_assurance.models import AuditReadinessAssessment
from app.control_assurance.schemas import ASSURANCE_ONLY_FLAGS


class AuditReadinessAssessmentEngine:
    """Assess future audit review readiness."""

    def assess(self, scorecard: dict[str, Any]) -> dict[str, Any]:
        score = round(
            (
                float(scorecard.get("control_quality_score", 0))
                + float(scorecard.get("evidence_sufficiency_score", 0))
                + float(scorecard.get("owner_clarity_score", 0))
                + float(scorecard.get("policy_completeness_score", 0))
                + float(scorecard.get("gate_maturity_score", 0))
            )
            / 5,
            2,
        )
        payload = AuditReadinessAssessment(
            audit_readiness_score=score,
            status="جيد" if score >= 80 else "يحتاج تحسين",
            blockers=[] if score >= 80 else ["Improve assurance score"],
        ).to_dict()
        payload.update(ASSURANCE_ONLY_FLAGS)
        return payload
