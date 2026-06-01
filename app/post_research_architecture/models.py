"""Models for post-research strategic architecture outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.post_research_architecture.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class SerializableModel:
    """Small dataclass serialization helper."""

    schema_version: str = SCHEMA_VERSION
    architecture_only: bool = True
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class PostResearchRoadmap(SerializableModel):
    roadmap_id: str = "post-research-roadmap"
    created_at: str = "deterministic-post-research-architecture"
    current_platform_state: str = "Research Platform v1.0"
    next_program_name: str = "Trading System Architecture Program"
    roadmap_stages: list[str] | None = None
    forbidden_shortcuts: list[str] | None = None
    recommended_sequence: list[str] | None = None
    safety_notes: list[str] | None = None


@dataclass(frozen=True)
class StrategicGapAnalysis(SerializableModel):
    gap_id: str = "strategic-gap-analysis"
    current_capabilities: list[str] | None = None
    missing_capabilities: list[str] | None = None
    technical_gaps: list[dict[str, Any]] | None = None
    operational_gaps: list[str] | None = None
    safety_gaps: list[str] | None = None
    production_gaps: list[str] | None = None
    compliance_gaps: list[str] | None = None
    severity: str = "حرج"
    recommendations: list[str] | None = None


@dataclass(frozen=True)
class FutureExecutionBlueprint(SerializableModel):
    blueprint_id: str = "future-execution-blueprint"
    purpose: str = "Architecture document for a future isolated execution layer."
    required_components: list[str] | None = None
    forbidden_current_implementation: list[str] | None = None
    safety_controls: list[str] | None = None
    audit_requirements: list[str] | None = None
    failure_modes: list[str] | None = None
    prerequisites: list[str] | None = None
    not_implemented: bool = True


@dataclass(frozen=True)
class FutureBrokerIntegrationBlueprint(SerializableModel):
    blueprint_id: str = "future-broker-integration-blueprint"
    purpose: str = "Architecture document for a future broker isolation boundary."
    adapter_boundary: list[str] | None = None
    broker_isolation_rules: list[str] | None = None
    credential_safety_requirements: list[str] | None = None
    session_safety_requirements: list[str] | None = None
    prohibited_current_actions: list[str] | None = None
    required_preconditions: list[str] | None = None
    not_implemented: bool = True


@dataclass(frozen=True)
class FutureRiskArchitectureBlueprint(SerializableModel):
    blueprint_id: str = "future-risk-architecture-blueprint"
    risk_domains: list[str] | None = None
    hard_limits: list[str] | None = None
    kill_switch_requirements: list[str] | None = None
    max_loss_rules: list[str] | None = None
    drawdown_rules: list[str] | None = None
    exposure_rules: list[str] | None = None
    incident_response: list[str] | None = None
    audit_requirements: list[str] | None = None
    not_implemented: bool = True


@dataclass(frozen=True)
class FutureMonitoringArchitectureBlueprint(SerializableModel):
    blueprint_id: str = "future-monitoring-architecture-blueprint"
    monitoring_domains: list[str] | None = None
    health_checks: list[str] | None = None
    alerting_requirements: list[str] | None = None
    observability_requirements: list[str] | None = None
    logs: list[str] | None = None
    metrics: list[str] | None = None
    incident_review: list[str] | None = None
    not_implemented: bool = True


@dataclass(frozen=True)
class FutureGovernanceBlueprint(SerializableModel):
    blueprint_id: str = "future-governance-blueprint"
    approval_gates: list[str] | None = None
    human_review_requirements: list[str] | None = None
    audit_trails: list[str] | None = None
    change_control: list[str] | None = None
    release_control: list[str] | None = None
    safety_reviews: list[str] | None = None
    rollback_policy: list[str] | None = None
    not_implemented: bool = True


@dataclass(frozen=True)
class TransitionPlan(SerializableModel):
    transition_id: str = "post-research-transition-plan"
    recommended_next_program: str = "Trading System Architecture Program"
    required_decisions: list[str] | None = None
    required_documentation: list[str] | None = None
    required_validation: list[str] | None = None
    stop_conditions: list[str] | None = None
    forbidden_transitions: list[str] | None = None
    safe_transition_sequence: list[str] | None = None
    first_safe_next_step: str = ""


@dataclass(frozen=True)
class PostResearchBoundaryModel(SerializableModel):
    allowed_now: list[str] | None = None
    forbidden_now: list[str] | None = None
    future_only_not_current: list[str] | None = None
