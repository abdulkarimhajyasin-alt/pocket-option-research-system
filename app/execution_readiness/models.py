"""Typed models for research-only execution readiness."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


PASS = "PASS"
WARNING = "WARNING"
FAIL = "FAIL"

QUALIFICATION_VERY_QUALIFIED = "مؤهل جداً"
QUALIFICATION_QUALIFIED = "مؤهل"
QUALIFICATION_CONDITIONAL = "مؤهل بشروط"
QUALIFICATION_WEAK = "ضعيف"
QUALIFICATION_REJECTED = "مرفوض"


@dataclass(frozen=True)
class ExecutionCandidate:
    """One research signal candidate evaluated for future paper-execution readiness."""

    candidate_id: str
    signal_id: str
    asset: str
    direction: str
    confidence: float
    quality: float
    confluence: float
    readiness: float
    qualification: str
    timestamp: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "signal_id": self.signal_id,
            "asset": self.asset,
            "direction": self.direction,
            "confidence": self.confidence,
            "quality": self.quality,
            "confluence": self.confluence,
            "readiness": self.readiness,
            "qualification": self.qualification,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "research_only": True,
            "readiness_only": True,
            "not_execution": True,
            "not_order_placement": True,
        }


@dataclass(frozen=True)
class ExecutionReadinessResult:
    """Readiness score dimensions."""

    score: float
    signal_readiness: float
    confidence_readiness: float
    quality_readiness: float
    confluence_readiness: float
    regime_readiness: float
    pattern_readiness: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "signal_readiness": self.signal_readiness,
            "confidence_readiness": self.confidence_readiness,
            "quality_readiness": self.quality_readiness,
            "confluence_readiness": self.confluence_readiness,
            "regime_readiness": self.regime_readiness,
            "pattern_readiness": self.pattern_readiness,
        }


@dataclass(frozen=True)
class ExecutionQualificationResult:
    """Qualification distribution for readiness candidates."""

    score: float
    state: str
    distribution: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "state": self.state,
            "distribution": self.distribution,
        }


@dataclass(frozen=True)
class ExecutionGateResult:
    """One execution-readiness gate result."""

    name: str
    arabic_label: str
    state: str
    score: float
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arabic_label": self.arabic_label,
            "state": self.state,
            "score": self.score,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class ExecutionScoringResult:
    """Top-level execution-readiness scores."""

    readiness_score: float
    qualification_score: float
    confidence_score: float
    quality_score: float

    def to_dict(self) -> dict[str, float]:
        return {
            "readiness_score": self.readiness_score,
            "qualification_score": self.qualification_score,
            "confidence_score": self.confidence_score,
            "quality_score": self.quality_score,
        }


@dataclass(frozen=True)
class ExecutionValidationResult:
    """Validation dimensions for execution-readiness outputs."""

    score: float
    candidate_integrity: float
    readiness_integrity: float
    gate_consistency: float
    score_consistency: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "candidate_integrity": self.candidate_integrity,
            "readiness_integrity": self.readiness_integrity,
            "gate_consistency": self.gate_consistency,
            "score_consistency": self.score_consistency,
        }


@dataclass(frozen=True)
class ExecutionDiagnostic:
    """Arabic diagnostic for weak readiness dimensions."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class ExecutionRecommendation:
    """Arabic recommendation for readiness improvement."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class ExecutionReadinessRun:
    """Complete research-only execution readiness run."""

    timestamp: datetime
    candidates: tuple[ExecutionCandidate, ...]
    readiness: ExecutionReadinessResult
    qualification: ExecutionQualificationResult
    gates: tuple[ExecutionGateResult, ...]
    scoring: ExecutionScoringResult
    validation: ExecutionValidationResult
    diagnostics: tuple[ExecutionDiagnostic, ...]
    recommendations: tuple[ExecutionRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "candidates": [item.to_dict() for item in self.candidates],
            "readiness": self.readiness.to_dict(),
            "qualification": self.qualification.to_dict(),
            "gates": [item.to_dict() for item in self.gates],
            "scoring": self.scoring.to_dict(),
            "validation": self.validation.to_dict(),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "research_only": True,
            "readiness_only": True,
            "not_execution": True,
            "not_order_placement": True,
            "not_account_login": True,
            "not_broker_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_broker_control": True,
        }
