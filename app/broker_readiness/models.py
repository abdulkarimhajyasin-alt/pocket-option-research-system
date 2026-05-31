"""Typed models for passive broker observation readiness."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ObservationCapability:
    """Passive observation capability model."""

    market_visibility: float
    asset_visibility: float
    payout_visibility: float
    session_visibility: float
    candle_visibility: float
    signal_visibility: float

    @property
    def score(self) -> float:
        values = (
            self.market_visibility,
            self.asset_visibility,
            self.payout_visibility,
            self.session_visibility,
            self.candle_visibility,
            self.signal_visibility,
        )
        return round(sum(values) / len(values), 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "market_visibility": self.market_visibility,
            "asset_visibility": self.asset_visibility,
            "payout_visibility": self.payout_visibility,
            "session_visibility": self.session_visibility,
            "candle_visibility": self.candle_visibility,
            "signal_visibility": self.signal_visibility,
            "score": self.score,
            "research_only": True,
            "observation_only": True,
        }


@dataclass(frozen=True)
class RestrictionCheck:
    """Single safety restriction check."""

    name: str
    status: str
    status_ar: str
    explanation: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "status": self.status,
            "status_ar": self.status_ar,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class RestrictionReport:
    """Full safety restriction report."""

    checks: tuple[RestrictionCheck, ...]
    status: str
    status_ar: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": [item.to_dict() for item in self.checks],
            "status": self.status,
            "status_ar": self.status_ar,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Passive observation validation result."""

    score: float
    observation_architecture: float
    observation_data_flow: float
    observation_reporting: float
    observation_diagnostics: float
    observation_isolation: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "observation_architecture": self.observation_architecture,
            "observation_data_flow": self.observation_data_flow,
            "observation_reporting": self.observation_reporting,
            "observation_diagnostics": self.observation_diagnostics,
            "observation_isolation": self.observation_isolation,
        }


@dataclass(frozen=True)
class CapabilityAssessment:
    """Observation capability assessment."""

    score: float
    data_collection_capability: float
    observation_capability: float
    reporting_capability: float
    monitoring_capability: float
    diagnostics_capability: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "data_collection_capability": self.data_collection_capability,
            "observation_capability": self.observation_capability,
            "reporting_capability": self.reporting_capability,
            "monitoring_capability": self.monitoring_capability,
            "diagnostics_capability": self.diagnostics_capability,
        }


@dataclass(frozen=True)
class ReadinessScore:
    """Observation readiness score."""

    score: float
    state: str
    explanation: str
    architecture_readiness: float
    observation_readiness: float
    data_readiness: float
    monitoring_readiness: float
    safety_readiness: float
    restriction_compliance: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "architecture_readiness": self.architecture_readiness,
            "observation_readiness": self.observation_readiness,
            "data_readiness": self.data_readiness,
            "monitoring_readiness": self.monitoring_readiness,
            "safety_readiness": self.safety_readiness,
            "restriction_compliance": self.restriction_compliance,
            "observation_only": True,
            "not_execution": True,
        }


@dataclass(frozen=True)
class DiagnosticFinding:
    """Broker readiness diagnostic finding."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class BrokerRecommendation:
    """Arabic readiness recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class BrokerReadinessResult:
    """Full passive broker observation readiness result."""

    timestamp: datetime
    capability: ObservationCapability
    assessment: CapabilityAssessment
    validation: ValidationResult
    restrictions: RestrictionReport
    readiness: ReadinessScore
    diagnostics: tuple[DiagnosticFinding, ...]
    recommendations: tuple[BrokerRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "capability": self.capability.to_dict(),
            "assessment": self.assessment.to_dict(),
            "validation": self.validation.to_dict(),
            "restrictions": self.restrictions.to_dict(),
            "readiness": self.readiness.to_dict(),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "research_only": True,
            "observation_only": True,
            "not_execution": True,
            "not_order_placement": True,
            "not_account_action": True,
            "not_automation": True,
            "not_broker_control": True,
        }
