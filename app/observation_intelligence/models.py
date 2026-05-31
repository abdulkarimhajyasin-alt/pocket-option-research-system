"""Typed models for unified observation intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class UnifiedObservation:
    """Normalized observation from any passive observation source."""

    observation_id: str
    source_type: str
    source_name: str
    timestamp: str
    assets: float
    payouts: float
    sessions: float
    symbols: float
    market_data: float
    visibility_score: float
    quality_score: float
    confidence_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "timestamp": self.timestamp,
            "assets": self.assets,
            "payouts": self.payouts,
            "sessions": self.sessions,
            "symbols": self.symbols,
            "market_data": self.market_data,
            "visibility_score": self.visibility_score,
            "quality_score": self.quality_score,
            "confidence_score": self.confidence_score,
            "research_only": True,
            "observation_only": True,
        }


@dataclass(frozen=True)
class NormalizationResult:
    score: float
    source_count: int
    normalized_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "source_count": self.source_count,
            "normalized_count": self.normalized_count,
        }


@dataclass(frozen=True)
class AggregationResult:
    score: float
    coverage: float
    consistency: float
    visibility: float
    completeness: float
    confidence: float
    conflicts: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "coverage": self.coverage,
            "consistency": self.consistency,
            "visibility": self.visibility,
            "completeness": self.completeness,
            "confidence": self.confidence,
            "conflicts": self.conflicts,
        }


@dataclass(frozen=True)
class IntelligenceResult:
    score: float
    state: str
    explanation: str
    observation_quality: float
    observation_confidence: float
    observation_reliability: float
    observation_completeness: float
    observation_readiness: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "observation_quality": self.observation_quality,
            "observation_confidence": self.observation_confidence,
            "observation_reliability": self.observation_reliability,
            "observation_completeness": self.observation_completeness,
            "observation_readiness": self.observation_readiness,
        }


@dataclass(frozen=True)
class ValidationResult:
    score: float
    normalized_structure: float
    source_compatibility: float
    completeness: float
    consistency: float
    integrity: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "normalized_structure": self.normalized_structure,
            "source_compatibility": self.source_compatibility,
            "completeness": self.completeness,
            "consistency": self.consistency,
            "integrity": self.integrity,
        }


@dataclass(frozen=True)
class ConfidenceResult:
    score: float
    source_confidence: float
    data_confidence: float
    visibility_confidence: float
    consistency_confidence: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "source_confidence": self.source_confidence,
            "data_confidence": self.data_confidence,
            "visibility_confidence": self.visibility_confidence,
            "consistency_confidence": self.consistency_confidence,
        }


@dataclass(frozen=True)
class QualityResult:
    score: float
    visibility: float
    completeness: float
    consistency: float
    freshness: float
    reliability: float

    def to_dict(self) -> dict[str, float]:
        return {
            "score": self.score,
            "visibility": self.visibility,
            "completeness": self.completeness,
            "consistency": self.consistency,
            "freshness": self.freshness,
            "reliability": self.reliability,
        }


@dataclass(frozen=True)
class ObservationDiagnostic:
    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class ObservationRecommendation:
    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class ObservationIntelligenceResult:
    timestamp: datetime
    observations: tuple[UnifiedObservation, ...]
    normalization: NormalizationResult
    aggregation: AggregationResult
    validation: ValidationResult
    confidence: ConfidenceResult
    quality: QualityResult
    intelligence: IntelligenceResult
    diagnostics: tuple[ObservationDiagnostic, ...]
    recommendations: tuple[ObservationRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "observations": [item.to_dict() for item in self.observations],
            "normalization": self.normalization.to_dict(),
            "aggregation": self.aggregation.to_dict(),
            "validation": self.validation.to_dict(),
            "confidence": self.confidence.to_dict(),
            "quality": self.quality.to_dict(),
            "intelligence": self.intelligence.to_dict(),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "research_only": True,
            "observation_only": True,
            "not_execution": True,
            "not_order_placement": True,
            "not_account_login": True,
            "not_broker_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_broker_control": True,
        }
