"""Models for operational governance framework artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.operational_governance.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class SerializableModel:
    """Small dataclass serialization helper."""

    schema_version: str = SCHEMA_VERSION
    governance_only: bool = True
    design_only: bool = True
    architecture_only: bool = True
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class GovernanceItem(SerializableModel):
    item_id: str = ""
    title: str = ""
    description: str = ""
    category: str = ""
    priority: str = "متوسط"
    status: str = "موثق"
    implementation_allowed_now: bool = False
    future_program_required: bool = True
    safety_notes: list[str] | None = None
    verification_method: str = "governance review"


@dataclass(frozen=True)
class GovernanceCategory(SerializableModel):
    category_id: str = ""
    title: str = ""
    status: str = "موثق"
    items: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class AuthorityRole(GovernanceCategory):
    pass


@dataclass(frozen=True)
class ApprovalWorkflow(GovernanceCategory):
    pass


@dataclass(frozen=True)
class ChangeControl(GovernanceCategory):
    pass


@dataclass(frozen=True)
class ReleaseGovernancePlan(GovernanceCategory):
    pass


@dataclass(frozen=True)
class IncidentEscalationPlan(GovernanceCategory):
    pass


@dataclass(frozen=True)
class KillSwitchGovernancePlan(GovernanceCategory):
    pass


@dataclass(frozen=True)
class AuditControl(GovernanceCategory):
    pass


@dataclass(frozen=True)
class OperatorResponsibility(GovernanceCategory):
    pass


@dataclass(frozen=True)
class ReviewBoard(GovernanceCategory):
    pass


@dataclass(frozen=True)
class DecisionAuthorityRule(GovernanceCategory):
    pass


@dataclass(frozen=True)
class ControlEvidenceRequirement(GovernanceCategory):
    pass


@dataclass(frozen=True)
class OperationalPolicy(GovernanceCategory):
    pass


@dataclass(frozen=True)
class GovernanceReadinessGate(SerializableModel):
    gate_id: str = ""
    title: str = ""
    required: bool = True
    current_status: str = "missing"
    blocks_progress: bool = True
    may_approve_live_trading: bool = False


@dataclass(frozen=True)
class OperationalGovernanceSummary(SerializableModel):
    governance_status: str = "Governance Incomplete"
    governance_domain_count: int = 0
    authority_role_count: int = 0
    approval_workflow_count: int = 0
    readiness_state: str = "Not Ready"
    diagnostic_count: int = 0
    recommendation_count: int = 0


@dataclass(frozen=True)
class OperationalGovernanceDiagnostics(SerializableModel):
    code: str = ""
    severity: str = "متوسط"
    message: str = ""


@dataclass(frozen=True)
class OperationalGovernanceRecommendation(SerializableModel):
    recommendation_id: str = ""
    text: str = ""
    priority: str = "متوسط"


def governance_category(
    model,
    category_id: str,
    title: str,
    topics: list[str],
) -> GovernanceCategory:
    """Create a governance category with standard local-only items."""
    items = [
        GovernanceItem(
            item_id=f"{category_id.upper()}-{index:02d}",
            title=topic,
            description=f"Governance-only framework item for {topic.lower()}.",
            category=category_id,
            priority="مرتفع" if index <= 2 else "متوسط",
            safety_notes=[
                "Governance artifact only.",
                "No runtime control or external connectivity is allowed.",
            ],
        ).to_dict()
        for index, topic in enumerate(topics, 1)
    ]
    return model(category_id=category_id, title=title, items=items)
