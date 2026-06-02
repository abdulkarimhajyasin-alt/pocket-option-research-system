"""Models for review board simulation and gate dry runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.review_board_simulation.schemas import SCHEMA_VERSION, SIMULATION_ONLY_FLAGS


@dataclass(frozen=True)
class SerializableModel:
    """Small dataclass serialization helper."""

    schema_version: str = SCHEMA_VERSION
    simulation_only: bool = True
    review_only: bool = True
    dry_run_only: bool = True
    governance_only: bool = True
    design_only: bool = True
    architecture_only: bool = True
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ReviewBoardCriterion(SerializableModel):
    criterion_id: str = ""
    name: str = ""
    evidence_expectations: list[str] = field(default_factory=list)
    required_sources: list[str] = field(default_factory=list)
    weight: float = 1.0


@dataclass(frozen=True)
class ReviewBoard(SerializableModel):
    board_id: str = ""
    board_name: str = ""
    responsibilities: list[str] = field(default_factory=list)
    criteria: list[dict[str, Any]] = field(default_factory=list)
    forbidden_approvals: list[str] = field(default_factory=list)
    safety_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BlockerFinding(SerializableModel):
    blocker_id: str = ""
    scope: str = ""
    severity: str = "متوسط"
    description: str = ""
    remediation: str = ""


@dataclass(frozen=True)
class EvidenceReviewResult(SerializableModel):
    evidence_id: str = ""
    source_group: str = ""
    available_files: int = 0
    readiness_state: str = "Requires Human Review"
    missing_evidence: list[str] = field(default_factory=list)
    weak_evidence: list[str] = field(default_factory=list)
    linkage_score: float = 0.0


@dataclass(frozen=True)
class SimulatedDecision(SerializableModel):
    decision_id: str = ""
    board_name: str = ""
    gate_name: str = ""
    simulated_state: str = "Requires Human Review"
    rationale: str = ""
    evidence_reviewed: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    required_human_review: bool = True
    safety_notes: list[str] = field(default_factory=list)
    forbidden_real_world_use: bool = True


@dataclass(frozen=True)
class ReviewBoardSimulationResult(SerializableModel):
    board_name: str = ""
    criteria_results: list[dict[str, Any]] = field(default_factory=list)
    simulated_decisions: list[dict[str, Any]] = field(default_factory=list)
    blockers: list[dict[str, Any]] = field(default_factory=list)
    readiness_score: float = 0.0
    readiness_status: str = "غير جاهز"


@dataclass(frozen=True)
class DecisionGateDryRun(SerializableModel):
    gate_name: str = ""
    simulated_state: str = "Requires Human Review"
    readiness_score: float = 0.0
    evidence_reviewed: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    required_human_review: bool = True
    forbidden_real_world_use: bool = True


@dataclass(frozen=True)
class BoardReadinessScore(SerializableModel):
    board_name: str = ""
    score: float = 0.0
    status: str = "غير جاهز"


@dataclass(frozen=True)
class GateReadinessScore(SerializableModel):
    gate_name: str = ""
    score: float = 0.0
    status: str = "غير جاهز"


@dataclass(frozen=True)
class ReviewSimulationSummary(SerializableModel):
    simulation_status: str = "Requires Human Review"
    overall_review_readiness_score: float = 0.0
    simulated_decision_count: int = 0
    blocker_count: int = 0
    condition_count: int = 0
    required_human_review_count: int = 0


@dataclass(frozen=True)
class ReviewSimulationDiagnostic(SerializableModel):
    code: str = ""
    severity: str = "متوسط"
    message: str = ""


@dataclass(frozen=True)
class ReviewSimulationRecommendation(SerializableModel):
    recommendation_id: str = ""
    text: str = ""
    priority: str = "متوسط"


def safety_notes() -> list[str]:
    return [
        "Simulation artifact only.",
        "Review-board dry run only.",
        "No real-world approval, operational control, or account interaction is permitted.",
    ]


def with_flags(payload: dict[str, Any]) -> dict[str, Any]:
    return {**payload, **SIMULATION_ONLY_FLAGS}
