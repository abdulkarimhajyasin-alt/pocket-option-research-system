"""Typed models for strategy readiness evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class StrategyReadinessScore:
    """Research maturity score, not a deployment approval."""

    score: float
    state: str
    explanation: str
    components: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "components": self.components,
            "research_only": True,
            "not_deployment_approval": True,
        }


@dataclass(frozen=True)
class DeploymentGate:
    """Single deployment-gate research check."""

    name: str
    status: str
    status_ar: str
    score: float
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "status_ar": self.status_ar,
            "score": self.score,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class GateRequirementReport:
    """Configurable gate requirement result."""

    minimum_signal_count: int
    minimum_validation_count: int
    minimum_confidence_accuracy: float
    minimum_consistency_score: float
    minimum_readiness_score: float
    passed: bool
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "minimum_signal_count": self.minimum_signal_count,
            "minimum_validation_count": self.minimum_validation_count,
            "minimum_confidence_accuracy": self.minimum_confidence_accuracy,
            "minimum_consistency_score": self.minimum_consistency_score,
            "minimum_readiness_score": self.minimum_readiness_score,
            "passed": self.passed,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class ResearchStabilityScore:
    """Research stability score from consistency and reliability metrics."""

    score: float
    consistency: float
    variance: float
    repeatability: float
    confidence_reliability: float
    signal_reliability: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "consistency": self.consistency,
            "variance": self.variance,
            "repeatability": self.repeatability,
            "confidence_reliability": self.confidence_reliability,
            "signal_reliability": self.signal_reliability,
        }


@dataclass(frozen=True)
class DiagnosticItem:
    """Single deterministic diagnostic finding."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class DiagnosticsReport:
    """Strategy diagnostics report."""

    items: tuple[DiagnosticItem, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"items": [item.to_dict() for item in self.items]}


@dataclass(frozen=True)
class Recommendation:
    """Deterministic Arabic improvement recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class StrategyReadinessResult:
    """Full strategy readiness evaluation result."""

    strategy_id: str
    timestamp: datetime
    readiness: StrategyReadinessScore
    gates: tuple[DeploymentGate, ...]
    requirements: GateRequirementReport
    stability: ResearchStabilityScore
    diagnostics: DiagnosticsReport
    recommendations: tuple[Recommendation, ...]
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "timestamp": self.timestamp.isoformat(),
            "readiness": self.readiness.to_dict(),
            "gates": [gate.to_dict() for gate in self.gates],
            "requirements": self.requirements.to_dict(),
            "stability": self.stability.to_dict(),
            "diagnostics": self.diagnostics.to_dict(),
            "recommendations": [item.to_dict() for item in self.recommendations],
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "metadata": self.metadata,
            "research_only": True,
            "not_execution": True,
            "not_deployment_approval": True,
            "not_investment_advice": True,
        }
