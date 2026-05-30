"""Typed models for multi-timeframe confirmation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TimeframeState:
    timeframe: str
    state: str
    confidence: float
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "timeframe": self.timeframe,
            "state": self.state,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class StructureAlignmentResult:
    state: str
    state_ar: str
    pair_scores: dict[str, float]
    full_alignment_score: float
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "state_ar": self.state_ar,
            "pair_scores": self.pair_scores,
            "full_alignment_score": self.full_alignment_score,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class TrendAlignmentResult:
    score: float
    directional_agreement: float
    trend_strength: float
    trend_consistency: float
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "directional_agreement": self.directional_agreement,
            "trend_strength": self.trend_strength,
            "trend_consistency": self.trend_consistency,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class ConflictReport:
    has_conflict: bool
    severity: str
    conflicts: list[str]
    score_penalty: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_conflict": self.has_conflict,
            "severity": self.severity,
            "conflicts": self.conflicts,
            "score_penalty": self.score_penalty,
        }


@dataclass(frozen=True)
class MultiTimeframeScore:
    score: float
    reasoning: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "reasoning": self.reasoning,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
        }


@dataclass(frozen=True)
class ConfirmationResult:
    opportunity_id: str
    asset: str
    classification: str
    timestamp: datetime
    timeframe_states: tuple[TimeframeState, ...]
    alignment: StructureAlignmentResult
    trend: TrendAlignmentResult
    conflict: ConflictReport
    score: MultiTimeframeScore
    confirmation_score: float
    confirmation_state: str
    supporting_factors: list[str]
    conflicting_factors: list[str]
    alignment_explanation: str
    session: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "asset": self.asset,
            "classification": self.classification,
            "timestamp": self.timestamp.isoformat(),
            "timeframe_states": [item.to_dict() for item in self.timeframe_states],
            "alignment": self.alignment.to_dict(),
            "trend": self.trend.to_dict(),
            "conflict": self.conflict.to_dict(),
            "score": self.score.to_dict(),
            "confirmation_score": self.confirmation_score,
            "confirmation_state": self.confirmation_state,
            "supporting_factors": self.supporting_factors,
            "conflicting_factors": self.conflicting_factors,
            "alignment_explanation": self.alignment_explanation,
            "session": self.session,
            "metadata": self.metadata,
            "research_only": True,
        }
