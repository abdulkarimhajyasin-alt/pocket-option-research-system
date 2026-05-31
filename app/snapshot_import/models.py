"""Typed models for manual snapshot imports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


SUPPORTED_IMPORT_TYPES = (
    "html_snapshot",
    "dom_export",
    "page_capture",
    "observation_dump",
    "static_snapshot",
    "json_snapshot",
)


@dataclass(frozen=True)
class SnapshotImport:
    """Manually supplied snapshot import record."""

    import_id: str
    filename: str
    import_type: str
    source_path: str
    imported_at: str
    size_bytes: int
    validation_status: str
    processing_status: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "import_id": self.import_id,
            "filename": self.filename,
            "import_type": self.import_type,
            "source_path": self.source_path,
            "imported_at": self.imported_at,
            "size_bytes": self.size_bytes,
            "validation_status": self.validation_status,
            "processing_status": self.processing_status,
            "metadata": self.metadata,
            "manual_only": True,
            "research_only": True,
            "observation_only": True,
            "read_only": True,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Snapshot import validation result."""

    score: float
    file_structure: float
    file_integrity: float
    supported_type: float
    file_completeness: float
    size_constraints: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "file_structure": self.file_structure,
            "file_integrity": self.file_integrity,
            "supported_type": self.supported_type,
            "file_completeness": self.file_completeness,
            "size_constraints": self.size_constraints,
        }


@dataclass(frozen=True)
class ParseResult:
    """Visible information parsed from imported snapshots."""

    score: float
    assets: int
    payouts: int
    sessions: int
    timestamps: int
    market_information: int
    symbols: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "assets": self.assets,
            "payouts": self.payouts,
            "sessions": self.sessions,
            "timestamps": self.timestamps,
            "market_information": self.market_information,
            "symbols": self.symbols,
        }


@dataclass(frozen=True)
class ProcessingResult:
    """Snapshot processing result."""

    score: float
    parsed_data: float
    visibility_metrics: float
    completeness_metrics: float
    quality_metrics: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "parsed_data": self.parsed_data,
            "visibility_metrics": self.visibility_metrics,
            "completeness_metrics": self.completeness_metrics,
            "quality_metrics": self.quality_metrics,
        }


@dataclass(frozen=True)
class QualityResult:
    """Snapshot quality result."""

    score: float
    quality: float
    visibility: float
    completeness: float
    consistency: float
    freshness: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "quality": self.quality,
            "visibility": self.visibility,
            "completeness": self.completeness,
            "consistency": self.consistency,
            "freshness": self.freshness,
        }


@dataclass(frozen=True)
class SafetyStatus:
    """Manual snapshot import safety status."""

    status: str
    status_ar: str
    score: float
    no_login: bool
    no_authentication: bool
    no_browser_automation: bool
    no_broker_access: bool
    no_execution: bool
    no_account_interaction: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "status_ar": self.status_ar,
            "score": self.score,
            "no_login": self.no_login,
            "no_authentication": self.no_authentication,
            "no_browser_automation": self.no_browser_automation,
            "no_broker_access": self.no_broker_access,
            "no_execution": self.no_execution,
            "no_account_interaction": self.no_account_interaction,
        }


@dataclass(frozen=True)
class WorkflowScore:
    """Manual snapshot import workflow score."""

    score: float
    state: str
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "manual_only": True,
            "observation_only": True,
            "not_execution": True,
        }


@dataclass(frozen=True)
class SnapshotDiagnostic:
    """Manual snapshot import diagnostic finding."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class SnapshotRecommendation:
    """Arabic manual snapshot import recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class SnapshotImportResult:
    """Full manual snapshot import workflow result."""

    timestamp: datetime
    imports: tuple[SnapshotImport, ...]
    validation: ValidationResult
    parse: ParseResult
    processing: ProcessingResult
    quality: QualityResult
    safety: SafetyStatus
    workflow: WorkflowScore
    diagnostics: tuple[SnapshotDiagnostic, ...]
    recommendations: tuple[SnapshotRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "imports": [item.to_dict() for item in self.imports],
            "validation": self.validation.to_dict(),
            "parse": self.parse.to_dict(),
            "processing": self.processing.to_dict(),
            "quality": self.quality.to_dict(),
            "safety": self.safety.to_dict(),
            "workflow": self.workflow.to_dict(),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "manual_only": True,
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
