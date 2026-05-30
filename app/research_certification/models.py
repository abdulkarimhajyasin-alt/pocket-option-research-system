"""Typed models for research certification."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class CertificationScore:
    """Certification score, state, and component scores."""

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
class RequirementCheck:
    """Single configurable certification requirement result."""

    name: str
    value: float
    threshold: float
    status: str
    status_ar: str
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "threshold": self.threshold,
            "status": self.status,
            "status_ar": self.status_ar,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class RequirementsReport:
    """Full requirements report."""

    checks: tuple[RequirementCheck, ...]
    passed: bool
    warnings: int
    failures: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": [item.to_dict() for item in self.checks],
            "passed": self.passed,
            "warnings": self.warnings,
            "failures": self.failures,
        }


@dataclass(frozen=True)
class ResearchRobustnessScore:
    """Robustness score for certification."""

    score: float
    repeatability: float
    variance: float
    reliability: float
    adaptability: float
    regime_resilience: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "repeatability": self.repeatability,
            "variance": self.variance,
            "reliability": self.reliability,
            "adaptability": self.adaptability,
            "regime_resilience": self.regime_resilience,
        }


@dataclass(frozen=True)
class ResearchConsistencyScore:
    """Consistency score for certification."""

    score: float
    signal_consistency: float
    opportunity_consistency: float
    confluence_consistency: float
    lifecycle_consistency: float
    benchmark_consistency: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "signal_consistency": self.signal_consistency,
            "opportunity_consistency": self.opportunity_consistency,
            "confluence_consistency": self.confluence_consistency,
            "lifecycle_consistency": self.lifecycle_consistency,
            "benchmark_consistency": self.benchmark_consistency,
        }


@dataclass(frozen=True)
class ResearchStabilityScore:
    """Stability score for certification."""

    score: float
    score_stability: float
    quality_stability: float
    confidence_stability: float
    pattern_stability: float
    regime_stability: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "score_stability": self.score_stability,
            "quality_stability": self.quality_stability,
            "confidence_stability": self.confidence_stability,
            "pattern_stability": self.pattern_stability,
            "regime_stability": self.regime_stability,
        }


@dataclass(frozen=True)
class DiagnosticFinding:
    """Certification diagnostic finding."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class CertificationRecommendation:
    """Prioritized Arabic certification recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class ResearchMaturityScore:
    """Research maturity score."""

    score: float
    architecture_maturity: float
    validation_maturity: float
    data_maturity: float
    pattern_maturity: float
    certification_readiness: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "architecture_maturity": self.architecture_maturity,
            "validation_maturity": self.validation_maturity,
            "data_maturity": self.data_maturity,
            "pattern_maturity": self.pattern_maturity,
            "certification_readiness": self.certification_readiness,
        }


@dataclass(frozen=True)
class ResearchCertificationResult:
    """Full research certification result."""

    timestamp: datetime
    certification: CertificationScore
    requirements: RequirementsReport
    robustness: ResearchRobustnessScore
    consistency: ResearchConsistencyScore
    stability: ResearchStabilityScore
    maturity: ResearchMaturityScore
    diagnostics: tuple[DiagnosticFinding, ...]
    recommendations: tuple[CertificationRecommendation, ...]
    sample_size: int
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "certification": self.certification.to_dict(),
            "requirements": self.requirements.to_dict(),
            "robustness": self.robustness.to_dict(),
            "consistency": self.consistency.to_dict(),
            "stability": self.stability.to_dict(),
            "maturity": self.maturity.to_dict(),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "sample_size": self.sample_size,
            "metadata": self.metadata,
            "research_only": True,
            "not_execution": True,
            "not_deployment_approval": True,
            "not_broker_control": True,
            "not_account_interaction": True,
            "not_investment_advice": True,
            "not_profitability_claim": True,
        }
