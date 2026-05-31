"""Typed models for read-only browser observation artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


SUPPORTED_ARTIFACT_TYPES = (
    "html_snapshot",
    "dom_export",
    "page_capture",
    "observation_dump",
    "static_snapshot",
)


@dataclass(frozen=True)
class ObservationArtifact:
    """Externally supplied read-only browser observation artifact."""

    artifact_id: str
    artifact_type: str
    artifact_source: str
    created_at: str
    validation_status: str
    visibility_status: str
    monitoring_status: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "artifact_source": self.artifact_source,
            "created_at": self.created_at,
            "validation_status": self.validation_status,
            "visibility_status": self.visibility_status,
            "monitoring_status": self.monitoring_status,
            "metadata": self.metadata,
            "research_only": True,
            "observation_only": True,
        }


@dataclass(frozen=True)
class ParseResult:
    """Parsed observable fields from read-only artifacts."""

    score: float
    visible_assets: int
    visible_payouts: int
    visible_sessions: int
    visible_symbols: int
    visible_timestamps: int
    visible_market_data: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "visible_assets": self.visible_assets,
            "visible_payouts": self.visible_payouts,
            "visible_sessions": self.visible_sessions,
            "visible_symbols": self.visible_symbols,
            "visible_timestamps": self.visible_timestamps,
            "visible_market_data": self.visible_market_data,
        }


@dataclass(frozen=True)
class VisibilityResult:
    """Visibility assessment for parsed artifacts."""

    score: float
    observable_coverage: float
    field_completeness: float
    data_visibility: float
    report_visibility: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "observable_coverage": self.observable_coverage,
            "field_completeness": self.field_completeness,
            "data_visibility": self.data_visibility,
            "report_visibility": self.report_visibility,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Artifact validation result."""

    score: float
    structure: float
    completeness: float
    integrity: float
    consistency: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "structure": self.structure,
            "completeness": self.completeness,
            "integrity": self.integrity,
            "consistency": self.consistency,
        }


@dataclass(frozen=True)
class MonitoringResult:
    """Artifact monitoring result."""

    score: float
    quality: float
    stability: float
    consistency: float
    freshness: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "quality": self.quality,
            "stability": self.stability,
            "consistency": self.consistency,
            "freshness": self.freshness,
        }


@dataclass(frozen=True)
class SafetyStatus:
    """Read-only safety status."""

    status: str
    status_ar: str
    score: float
    no_login: bool
    no_authentication: bool
    no_browser_control: bool
    no_execution: bool
    no_order_apis: bool
    no_account_access: bool
    no_automation: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "status_ar": self.status_ar,
            "score": self.score,
            "no_login": self.no_login,
            "no_authentication": self.no_authentication,
            "no_browser_control": self.no_browser_control,
            "no_execution": self.no_execution,
            "no_order_apis": self.no_order_apis,
            "no_account_access": self.no_account_access,
            "no_automation": self.no_automation,
        }


@dataclass(frozen=True)
class AdapterScore:
    """Read-only browser observation adapter readiness."""

    score: float
    state: str
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "observation_only": True,
            "read_only": True,
            "not_execution": True,
        }


@dataclass(frozen=True)
class BrowserObservationDiagnostic:
    """Browser observation diagnostic finding."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class BrowserObservationRecommendation:
    """Arabic browser observation recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class BrowserObservationResult:
    """Full read-only browser observation result."""

    timestamp: datetime
    artifacts: tuple[ObservationArtifact, ...]
    parse: ParseResult
    validation: ValidationResult
    visibility: VisibilityResult
    monitoring: MonitoringResult
    safety: SafetyStatus
    adapter: AdapterScore
    diagnostics: tuple[BrowserObservationDiagnostic, ...]
    recommendations: tuple[BrowserObservationRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "artifacts": [item.to_dict() for item in self.artifacts],
            "parse": self.parse.to_dict(),
            "validation": self.validation.to_dict(),
            "visibility": self.visibility.to_dict(),
            "monitoring": self.monitoring.to_dict(),
            "safety": self.safety.to_dict(),
            "adapter": self.adapter.to_dict(),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "research_only": True,
            "observation_only": True,
            "read_only": True,
            "not_execution": True,
            "not_order_placement": True,
            "not_account_login": True,
            "not_broker_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_broker_control": True,
        }
