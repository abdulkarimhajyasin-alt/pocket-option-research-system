"""Typed models for strategy benchmark research."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class BenchmarkProfile:
    """Configuration profile used for research-only comparison."""

    profile_id: str
    profile_name: str
    profile_description: str
    weights: dict[str, float]
    thresholds: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "profile_name": self.profile_name,
            "profile_description": self.profile_description,
            "weights": self.weights,
            "thresholds": self.thresholds,
            "metadata": self.metadata,
            "research_only": True,
        }


@dataclass(frozen=True)
class ComparisonResult:
    """Profile comparison result across research-quality metrics."""

    profile: BenchmarkProfile
    readiness_score: float
    stability_score: float
    consistency_score: float
    confidence_accuracy: float
    signal_quality: float
    opportunity_quality: float
    confluence_quality: float
    adjusted_metrics: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile.to_dict(),
            "readiness_score": self.readiness_score,
            "stability_score": self.stability_score,
            "consistency_score": self.consistency_score,
            "confidence_accuracy": self.confidence_accuracy,
            "signal_quality": self.signal_quality,
            "opportunity_quality": self.opportunity_quality,
            "confluence_quality": self.confluence_quality,
            "adjusted_metrics": self.adjusted_metrics,
            "research_only": True,
            "not_trading_recommendation": True,
        }


@dataclass(frozen=True)
class BenchmarkScore:
    """Composite benchmark score on a 0-100 scale."""

    profile_id: str
    score: float
    state: str
    explanation: str
    components: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "components": self.components,
            "research_only": True,
        }


@dataclass(frozen=True)
class ImprovementReport:
    """Research comparison against the current strategy baseline."""

    profile_id: str
    status: str
    status_ar: str
    score_delta: float
    quality_delta: float
    stability_delta: float
    readiness_delta: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "status": self.status,
            "status_ar": self.status_ar,
            "score_delta": self.score_delta,
            "quality_delta": self.quality_delta,
            "stability_delta": self.stability_delta,
            "readiness_delta": self.readiness_delta,
        }


@dataclass(frozen=True)
class RobustnessScore:
    """Repeatability, stability, consistency, and variance score."""

    profile_id: str
    score: float
    repeatability: float
    stability: float
    consistency: float
    variance: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "score": self.score,
            "repeatability": self.repeatability,
            "stability": self.stability,
            "consistency": self.consistency,
            "variance": self.variance,
        }


@dataclass(frozen=True)
class StrategyRanking:
    """Ranked profile output."""

    rank: int
    profile_id: str
    profile_name: str
    score: float
    strengths: list[str]
    weaknesses: list[str]
    selection_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "profile_id": self.profile_id,
            "profile_name": self.profile_name,
            "score": self.score,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "selection_reason": self.selection_reason,
        }


@dataclass(frozen=True)
class BenchmarkRecommendation:
    """Prioritized Arabic benchmark recommendation."""

    title: str
    priority: str
    reason: str
    profile_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "priority": self.priority,
            "reason": self.reason,
            "profile_id": self.profile_id,
        }


@dataclass(frozen=True)
class CertificationPreparation:
    """Research certification preparation state, not approval."""

    state: str
    explanation: str
    not_deployment_approval: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "explanation": self.explanation,
            "not_deployment_approval": self.not_deployment_approval,
            "not_trading_recommendation": True,
        }


@dataclass(frozen=True)
class StrategyBenchmarkResult:
    """Full strategy benchmark result."""

    timestamp: datetime
    comparisons: tuple[ComparisonResult, ...]
    scores: tuple[BenchmarkScore, ...]
    robustness: tuple[RobustnessScore, ...]
    improvements: tuple[ImprovementReport, ...]
    rankings: tuple[StrategyRanking, ...]
    recommendations: tuple[BenchmarkRecommendation, ...]
    certification: CertificationPreparation
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "comparisons": [item.to_dict() for item in self.comparisons],
            "scores": [item.to_dict() for item in self.scores],
            "robustness": [item.to_dict() for item in self.robustness],
            "improvements": [item.to_dict() for item in self.improvements],
            "rankings": [item.to_dict() for item in self.rankings],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "certification": self.certification.to_dict(),
            "metadata": self.metadata,
            "research_only": True,
            "not_execution": True,
            "not_broker_control": True,
            "not_investment_advice": True,
            "not_profitability_claim": True,
        }
