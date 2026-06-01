"""Models for trading requirements and constraints documents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.trading_requirements.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class SerializableModel:
    """Small dataclass serialization helper."""

    schema_version: str = SCHEMA_VERSION
    requirements_only: bool = True
    architecture_only: bool = True
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class RequirementItem(SerializableModel):
    requirement_id: str = ""
    title: str = ""
    description: str = ""
    category: str = ""
    priority: str = "متوسط"
    status: str = "مطلوب"
    rationale: str = ""
    verification_method: str = "document review"
    implementation_allowed_now: bool = False
    requires_future_program: bool = True
    safety_notes: list[str] | None = None


@dataclass(frozen=True)
class ConstraintItem(SerializableModel):
    constraint_id: str = ""
    title: str = ""
    description: str = ""
    category: str = ""
    constraint_type: str = "hard"
    priority: str = "مرتفع"
    implementation_allowed_now: bool = False
    requires_future_program: bool = True
    safety_notes: list[str] | None = None


@dataclass(frozen=True)
class RequirementCategory(SerializableModel):
    category_id: str = ""
    title: str = ""
    items: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class ConstraintCategory(SerializableModel):
    category_id: str = ""
    title: str = ""
    items: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class GoNoGoCriterion(SerializableModel):
    criterion_id: str = ""
    title: str = ""
    required: bool = True
    current_status: str = "missing"
    blocks_progress: bool = True
    may_approve_live_trading: bool = False


@dataclass(frozen=True)
class RequirementSpecification(SerializableModel):
    specification_id: str = "trading-requirements-specification"
    categories: dict[str, Any] | None = None
    constraints: dict[str, Any] | None = None
    go_no_go: dict[str, Any] | None = None


@dataclass(frozen=True)
class RequirementCoverageSummary(SerializableModel):
    requirement_count: int = 0
    constraint_count: int = 0
    category_count: int = 0
    highest_priority: str = "مرتفع"
    go_no_go_state: str = "Requirements Incomplete"
    safety_requirement_count: int = 0
    risk_requirement_count: int = 0
    compliance_constraint_count: int = 0
    execution_constraint_count: int = 0
    broker_constraint_count: int = 0


@dataclass(frozen=True)
class RequirementDiagnostics(SerializableModel):
    code: str = ""
    severity: str = "متوسط"
    message: str = ""


@dataclass(frozen=True)
class RequirementRecommendation(SerializableModel):
    recommendation_id: str = ""
    text: str = ""
    priority: str = "متوسط"
