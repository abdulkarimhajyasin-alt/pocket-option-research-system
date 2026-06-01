"""Models for control assurance and review readiness."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.control_assurance.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class SerializableModel:
    """Small dataclass serialization helper."""

    schema_version: str = SCHEMA_VERSION
    assurance_only: bool = True
    review_readiness_only: bool = True
    governance_only: bool = True
    design_only: bool = True
    architecture_only: bool = True
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class AssuranceItem(SerializableModel):
    item_id: str = ""
    source_area: str = ""
    assessment_type: str = ""
    score: float = 0.0
    status: str = "مقبول"
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    owner: str = ""
    safety_notes: list[str] = field(default_factory=list)
    verification_method: str = "assurance review"


@dataclass(frozen=True)
class ControlAssuranceResult(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class EvidenceAssessment(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class OwnerAssessment(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class PolicyAssessment(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class GateAssessment(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class WeaknessAssessment(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class AuditReadinessAssessment(SerializableModel):
    audit_readiness_score: float = 0.0
    status: str = "يحتاج تحسين"
    blockers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GovernanceReviewReadiness(SerializableModel):
    review_readiness_state: str = "Review Blocked"
    blocker_count: int = 0
    missing_evidence_count: int = 0
    weak_control_count: int = 0
    missing_owner_count: int = 0


@dataclass(frozen=True)
class AssuranceScorecard(SerializableModel):
    control_quality_score: float = 0.0
    evidence_sufficiency_score: float = 0.0
    owner_clarity_score: float = 0.0
    policy_completeness_score: float = 0.0
    gate_maturity_score: float = 0.0
    audit_readiness_score: float = 0.0
    governance_review_readiness_score: float = 0.0
    overall_assurance_score: float = 0.0
    score_status: str = "غير جاهز"


@dataclass(frozen=True)
class AssuranceDiagnostic(SerializableModel):
    code: str = ""
    severity: str = "متوسط"
    message: str = ""


@dataclass(frozen=True)
class AssuranceRecommendation(SerializableModel):
    recommendation_id: str = ""
    text: str = ""
    priority: str = "متوسط"


def assurance_item(
    index: int,
    source_area: str,
    assessment_type: str,
    score: float,
    owner: str,
    required_evidence: list[str],
    weaknesses: list[str] | None = None,
) -> dict[str, Any]:
    """Build a standard assurance assessment item."""
    if score >= 85:
        status = "قوي"
    elif score >= 70:
        status = "مقبول"
    elif score >= 50:
        status = "ضعيف"
    else:
        status = "غير جاهز"
    return AssuranceItem(
        item_id=f"ASSURE-{assessment_type.upper()}-{index:02d}",
        source_area=source_area,
        assessment_type=assessment_type,
        score=round(score, 2),
        status=status,
        strengths=["Documented local governance artifact"],
        weaknesses=weaknesses or [],
        required_evidence=required_evidence,
        missing_evidence=[],
        owner=owner,
        safety_notes=[
            "Assurance artifact only.",
            "No runtime control or external connectivity is allowed.",
        ],
    ).to_dict()
