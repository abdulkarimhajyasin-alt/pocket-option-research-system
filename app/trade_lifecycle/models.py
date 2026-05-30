"""Typed models for research lifecycle simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


LIFECYCLE_STATES = (
    "فرصة جديدة",
    "بانتظار التأكيد",
    "مؤهلة للدراسة",
    "قيد المحاكاة",
    "انتهت",
    "ناجحة",
    "خاسرة",
    "محايدة",
    "مرفوضة",
)


@dataclass(frozen=True)
class LifecycleTransition:
    """One deterministic lifecycle state transition."""

    from_state: str
    to_state: str
    timestamp: datetime
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_state": self.from_state,
            "to_state": self.to_state,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class LifecycleState:
    """Current lifecycle state plus transition history."""

    current: str
    transitions: tuple[LifecycleTransition, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "current": self.current,
            "transitions": [item.to_dict() for item in self.transitions],
        }


@dataclass(frozen=True)
class EntryAnalysis:
    timing_quality: float
    confirmation_quality: float
    entry_alignment: float
    readiness_score: float
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "timing_quality": self.timing_quality,
            "confirmation_quality": self.confirmation_quality,
            "entry_alignment": self.entry_alignment,
            "readiness_score": self.readiness_score,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class ExpiryAnalysis:
    expiry: str
    suitability: float
    outcome_sensitivity: float
    expiry_quality: float
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "expiry": self.expiry,
            "suitability": self.suitability,
            "outcome_sensitivity": self.outcome_sensitivity,
            "expiry_quality": self.expiry_quality,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class OutcomeEvaluation:
    outcome: str
    evaluation_reason: str
    confidence_accuracy: float
    confluence_accuracy: float
    qualification_accuracy: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "evaluation_reason": self.evaluation_reason,
            "confidence_accuracy": self.confidence_accuracy,
            "confluence_accuracy": self.confluence_accuracy,
            "qualification_accuracy": self.qualification_accuracy,
        }


@dataclass(frozen=True)
class PostTradeInsights:
    success_reasons: list[str]
    failure_reasons: list[str]
    strongest_factors: list[str]
    weakest_factors: list[str]
    recurring_patterns: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "success_reasons": self.success_reasons,
            "failure_reasons": self.failure_reasons,
            "strongest_factors": self.strongest_factors,
            "weakest_factors": self.weakest_factors,
            "recurring_patterns": self.recurring_patterns,
        }


@dataclass(frozen=True)
class FailureAnalysisReport:
    rejection_reasons: list[str]
    weak_confirmations: list[str]
    weak_confluence: list[str]
    timeframe_conflicts: list[str]
    liquidity_issues: list[str]
    session_issues: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "rejection_reasons": self.rejection_reasons,
            "weak_confirmations": self.weak_confirmations,
            "weak_confluence": self.weak_confluence,
            "timeframe_conflicts": self.timeframe_conflicts,
            "liquidity_issues": self.liquidity_issues,
            "session_issues": self.session_issues,
        }


@dataclass(frozen=True)
class SuccessAnalysisReport:
    strongest_confluence_factors: list[str]
    strongest_timeframe_alignment: list[str]
    strongest_session_alignment: list[str]
    strongest_liquidity_conditions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "strongest_confluence_factors": self.strongest_confluence_factors,
            "strongest_timeframe_alignment": self.strongest_timeframe_alignment,
            "strongest_session_alignment": self.strongest_session_alignment,
            "strongest_liquidity_conditions": self.strongest_liquidity_conditions,
        }


@dataclass(frozen=True)
class LifecycleQuality:
    score: float
    classification: str
    readiness: str
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "classification": self.classification,
            "readiness": self.readiness,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class TradeLifecycleRecord:
    lifecycle_id: str
    opportunity_id: str
    signal_id: str
    asset: str
    classification: str
    confidence: float
    confluence_score: float
    qualification_score: float
    timeframe_score: float
    session_score: float
    created_at: datetime
    completed_at: datetime | None
    state: LifecycleState
    outcome: OutcomeEvaluation
    entry: EntryAnalysis
    expiry: ExpiryAnalysis
    post_trade: PostTradeInsights
    failure_analysis: FailureAnalysisReport
    success_analysis: SuccessAnalysisReport
    quality: LifecycleQuality
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lifecycle_id": self.lifecycle_id,
            "opportunity_id": self.opportunity_id,
            "signal_id": self.signal_id,
            "asset": self.asset,
            "classification": self.classification,
            "confidence": self.confidence,
            "confluence_score": self.confluence_score,
            "qualification_score": self.qualification_score,
            "timeframe_score": self.timeframe_score,
            "session_score": self.session_score,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "state": self.state.to_dict(),
            "outcome": self.outcome.to_dict(),
            "entry": self.entry.to_dict(),
            "expiry": self.expiry.to_dict(),
            "post_trade": self.post_trade.to_dict(),
            "failure_analysis": self.failure_analysis.to_dict(),
            "success_analysis": self.success_analysis.to_dict(),
            "quality": self.quality.to_dict(),
            "metadata": self.metadata,
            "research_only": True,
            "not_execution": True,
            "not_investment_advice": True,
        }
