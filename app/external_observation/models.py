"""Typed models for the external observation sandbox."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


SUPPORTED_SOURCE_TYPES = (
    "simulated",
    "local_file",
    "historical_dataset",
    "sandbox_feed",
)


@dataclass(frozen=True)
class ObservationSource:
    """Passive observation source definition."""

    source_id: str
    source_name: str
    source_type: str
    observation_status: str
    visibility_scope: str
    validation_status: str
    isolation_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "observation_status": self.observation_status,
            "visibility_scope": self.visibility_scope,
            "validation_status": self.validation_status,
            "isolation_status": self.isolation_status,
            "research_only": True,
            "observation_only": True,
        }


@dataclass(frozen=True)
class SourceValidationResult:
    """Validation result for sandbox sources."""

    score: float
    structure: float
    integrity: float
    completeness: float
    consistency: float
    compatibility: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "structure": self.structure,
            "integrity": self.integrity,
            "completeness": self.completeness,
            "consistency": self.consistency,
            "compatibility": self.compatibility,
        }


@dataclass(frozen=True)
class IsolationStatus:
    """Isolation status for the sandbox."""

    status: str
    status_ar: str
    score: float
    no_broker_connectivity: bool
    no_account_access: bool
    no_execution_paths: bool
    no_authentication_flows: bool
    no_order_apis: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "status_ar": self.status_ar,
            "score": self.score,
            "no_broker_connectivity": self.no_broker_connectivity,
            "no_account_access": self.no_account_access,
            "no_execution_paths": self.no_execution_paths,
            "no_authentication_flows": self.no_authentication_flows,
            "no_order_apis": self.no_order_apis,
        }


@dataclass(frozen=True)
class MonitoringResult:
    """Passive source monitoring result."""

    score: float
    uptime: float
    quality: float
    consistency: float
    coverage: float
    stability: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "uptime": self.uptime,
            "quality": self.quality,
            "consistency": self.consistency,
            "coverage": self.coverage,
            "stability": self.stability,
        }


@dataclass(frozen=True)
class HealthResult:
    """Sandbox health result."""

    score: float
    state: str
    explanation: str
    validation_health: float
    monitoring_health: float
    isolation_health: float
    reporting_health: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "validation_health": self.validation_health,
            "monitoring_health": self.monitoring_health,
            "isolation_health": self.isolation_health,
            "reporting_health": self.reporting_health,
        }


@dataclass(frozen=True)
class SandboxScore:
    """Overall external observation sandbox score."""

    score: float
    state: str
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "observation_only": True,
            "not_execution": True,
        }


@dataclass(frozen=True)
class ObservationDiagnostic:
    """External observation diagnostic finding."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class ObservationRecommendation:
    """Arabic external observation recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class ExternalObservationResult:
    """Full external observation sandbox result."""

    timestamp: datetime
    sources: tuple[ObservationSource, ...]
    validation: SourceValidationResult
    isolation: IsolationStatus
    monitoring: MonitoringResult
    health: HealthResult
    sandbox: SandboxScore
    diagnostics: tuple[ObservationDiagnostic, ...]
    recommendations: tuple[ObservationRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "sources": [item.to_dict() for item in self.sources],
            "validation": self.validation.to_dict(),
            "isolation": self.isolation.to_dict(),
            "monitoring": self.monitoring.to_dict(),
            "health": self.health.to_dict(),
            "sandbox": self.sandbox.to_dict(),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "research_only": True,
            "observation_only": True,
            "not_execution": True,
            "not_order_placement": True,
            "not_account_login": True,
            "not_broker_authentication": True,
            "not_browser_automation": True,
            "not_broker_control": True,
        }
