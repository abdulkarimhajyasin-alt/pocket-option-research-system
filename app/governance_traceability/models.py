"""Models for governance traceability mappings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.governance_traceability.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class SerializableModel:
    """Small dataclass serialization helper."""

    schema_version: str = SCHEMA_VERSION
    traceability_only: bool = True
    governance_only: bool = True
    design_only: bool = True
    architecture_only: bool = True
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class TraceabilityItem(SerializableModel):
    mapping_id: str = ""
    source_area: str = ""
    target_control: str = ""
    mapping_type: str = ""
    strength: str = "متوسط"
    owner: str = ""
    evidence_required: list[str] | None = None
    status: str = "موثق"
    gaps: list[str] | None = None
    safety_notes: list[str] | None = None
    verification_method: str = "traceability review"


@dataclass(frozen=True)
class ControlMapping(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class EvidenceMapping(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ReadinessGateMapping(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class RiskControlMapping(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class IncidentControlMapping(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ReleaseControlMapping(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class MonitoringControlMapping(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class PolicyCoverageMapping(SerializableModel):
    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class TraceabilityCoverageSummary(SerializableModel):
    readiness_state: str = "Not Ready"
    mapped_design_areas: int = 0
    unmapped_design_areas: int = 0
    strong_mappings: int = 0
    weak_mappings: int = 0
    missing_controls: int = 0
    control_coverage_score: float = 0.0
    evidence_coverage_score: float = 0.0
    readiness_traceability_score: float = 0.0
    policy_coverage_score: float = 0.0
    overall_traceability_score: float = 0.0


@dataclass(frozen=True)
class TraceabilityDiagnostic(SerializableModel):
    code: str = ""
    severity: str = "متوسط"
    message: str = ""


@dataclass(frozen=True)
class TraceabilityRecommendation(SerializableModel):
    recommendation_id: str = ""
    text: str = ""
    priority: str = "متوسط"


def mapping_item(
    index: int,
    source_area: str,
    target_control: str,
    mapping_type: str,
    owner: str,
    evidence_required: list[str],
    strength: str = "قوي",
) -> dict[str, Any]:
    """Build a standard traceability mapping item."""
    return TraceabilityItem(
        mapping_id=f"TRACE-{mapping_type.upper()}-{index:02d}",
        source_area=source_area,
        target_control=target_control,
        mapping_type=mapping_type,
        strength=strength,
        owner=owner,
        evidence_required=evidence_required,
        gaps=[] if strength != "ضعيف" else ["Needs governance review"],
        safety_notes=[
            "Traceability artifact only.",
            "No runtime control or external connectivity is allowed.",
        ],
    ).to_dict()
