"""Typed models for adaptive pattern memory research."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class PatternMemoryRecord:
    """Single historical research pattern observation."""

    pattern_id: str
    asset: str
    session: str
    direction: str
    structure_state: str
    cisd_state: str
    fvg_state: str
    ifvg_state: str
    liquidity_state: str
    confluence_score: float
    timeframe_alignment: float
    opportunity_score: float
    confidence_score: float
    lifecycle_result: str
    performance_result: str
    timestamp: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def outcome_bucket(self) -> str:
        result = f"{self.lifecycle_result} {self.performance_result}".upper()
        if "WIN" in result or "ناجح" in result:
            return "successful"
        if "LOSS" in result or "فشل" in result or "خاسر" in result:
            return "failed"
        return "neutral"

    @property
    def signature(self) -> tuple[str, ...]:
        return (
            self.asset,
            self.session,
            self.direction,
            self.structure_state,
            self.cisd_state,
            self.fvg_state,
            self.ifvg_state,
            self.liquidity_state,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "asset": self.asset,
            "session": self.session,
            "direction": self.direction,
            "structure_state": self.structure_state,
            "cisd_state": self.cisd_state,
            "fvg_state": self.fvg_state,
            "ifvg_state": self.ifvg_state,
            "liquidity_state": self.liquidity_state,
            "confluence_score": self.confluence_score,
            "timeframe_alignment": self.timeframe_alignment,
            "opportunity_score": self.opportunity_score,
            "confidence_score": self.confidence_score,
            "lifecycle_result": self.lifecycle_result,
            "performance_result": self.performance_result,
            "outcome_bucket": self.outcome_bucket,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "research_only": True,
        }


@dataclass(frozen=True)
class DiscoveredPattern:
    """Recurring pattern discovered from memory."""

    pattern_key: str
    description: str
    occurrences: int
    success_count: int
    failure_count: int
    neutral_count: int
    stability: float
    pattern_score: float
    average_confluence: float
    average_opportunity: float
    average_confidence: float
    attributes: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_key": self.pattern_key,
            "description": self.description,
            "occurrences": self.occurrences,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "neutral_count": self.neutral_count,
            "stability": self.stability,
            "pattern_score": self.pattern_score,
            "average_confluence": self.average_confluence,
            "average_opportunity": self.average_opportunity,
            "average_confidence": self.average_confidence,
            "attributes": self.attributes,
            "research_only": True,
        }


@dataclass(frozen=True)
class SimilarityResult:
    """Similarity result against historical pattern memory."""

    record_id: str
    similarity_score: float
    category: str
    nearest_pattern: str
    historical_success_ratio: float
    confidence_adjustment: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "similarity_score": self.similarity_score,
            "category": self.category,
            "nearest_pattern": self.nearest_pattern,
            "historical_success_ratio": self.historical_success_ratio,
            "confidence_adjustment": self.confidence_adjustment,
        }


@dataclass(frozen=True)
class PatternQualityScore:
    """Pattern quality score on a 0-100 scale."""

    pattern_key: str
    score: float
    consistency: float
    stability: float
    reliability: float
    recurrence: float
    sample_size: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_key": self.pattern_key,
            "score": self.score,
            "consistency": self.consistency,
            "stability": self.stability,
            "reliability": self.reliability,
            "recurrence": self.recurrence,
            "sample_size": self.sample_size,
        }


@dataclass(frozen=True)
class LearningInsight:
    """Adaptive learning insight."""

    pattern_key: str
    category: str
    title: str
    detail: str
    adaptation_suggestion: str
    improvement_opportunity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_key": self.pattern_key,
            "category": self.category,
            "title": self.title,
            "detail": self.detail,
            "adaptation_suggestion": self.adaptation_suggestion,
            "improvement_opportunity": self.improvement_opportunity,
        }


@dataclass(frozen=True)
class PatternRanking:
    """Arabic ranking row for one pattern dimension."""

    category: str
    name: str
    rank: int
    score: float
    occurrences: int
    success_ratio: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "name": self.name,
            "rank": self.rank,
            "score": self.score,
            "occurrences": self.occurrences,
            "success_ratio": self.success_ratio,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class PatternMemoryResult:
    """Full adaptive pattern memory result."""

    timestamp: datetime
    records: tuple[PatternMemoryRecord, ...]
    discovered_patterns: tuple[DiscoveredPattern, ...]
    similarities: tuple[SimilarityResult, ...]
    quality_scores: tuple[PatternQualityScore, ...]
    learning_insights: tuple[LearningInsight, ...]
    rankings: tuple[PatternRanking, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "records": [item.to_dict() for item in self.records],
            "discovered_patterns": [
                item.to_dict() for item in self.discovered_patterns
            ],
            "similarities": [item.to_dict() for item in self.similarities],
            "quality_scores": [item.to_dict() for item in self.quality_scores],
            "learning_insights": [item.to_dict() for item in self.learning_insights],
            "rankings": [item.to_dict() for item in self.rankings],
            "metadata": self.metadata,
            "research_only": True,
            "not_execution": True,
            "not_broker_control": True,
            "not_account_interaction": True,
            "not_investment_advice": True,
            "not_profitability_claim": True,
        }
