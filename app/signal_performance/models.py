"""Typed models for signal performance validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PaperOutcome(str, Enum):
    """Historical research outcome for a classified signal."""

    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class TrackedSignal:
    """Signal intelligence output normalized for performance tracking."""

    signal_id: str
    asset: str
    classification: str
    confidence: float
    timestamp: datetime
    structure_state: str
    cisd_state: str
    fvg_state: str
    ifvg_state: str
    liquidity_state: str
    session_state: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "asset": self.asset,
            "classification": self.classification,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "structure_state": self.structure_state,
            "cisd_state": self.cisd_state,
            "fvg_state": self.fvg_state,
            "ifvg_state": self.ifvg_state,
            "liquidity_state": self.liquidity_state,
            "session_state": self.session_state,
            "metadata": self.metadata,
            "research_only": True,
        }


@dataclass(frozen=True)
class SignalOutcome:
    """Historical evaluation result for one tracked signal."""

    signal_id: str
    outcome: PaperOutcome
    candles_elapsed: int
    evaluation_timestamp: datetime
    evaluation_reason: str
    outcome_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "outcome": self.outcome.value,
            "outcome_ar": self.outcome_ar,
            "candles_elapsed": self.candles_elapsed,
            "evaluation_timestamp": self.evaluation_timestamp.isoformat(),
            "evaluation_reason": self.evaluation_reason,
            "outcome_score": self.outcome_score,
            "research_only": True,
        }

    @property
    def outcome_ar(self) -> str:
        labels = {
            PaperOutcome.WIN: "رابحة",
            PaperOutcome.LOSS: "خاسرة",
            PaperOutcome.BREAKEVEN: "تعادل",
            PaperOutcome.UNRESOLVED: "غير محسومة",
        }
        return labels[self.outcome]


@dataclass(frozen=True)
class PaperTradeResult:
    """Research-only paper result, not a trade or account simulation."""

    signal: TrackedSignal
    outcome: SignalOutcome
    entry_price: float
    evaluation_price: float
    movement: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal": self.signal.to_dict(),
            "outcome": self.outcome.to_dict(),
            "entry_price": self.entry_price,
            "evaluation_price": self.evaluation_price,
            "movement": self.movement,
            "research_only": True,
            "no_execution": True,
        }


@dataclass(frozen=True)
class ConfidenceValidationReport:
    """Validation of confidence buckets against historical outcomes."""

    buckets: dict[str, dict[str, float]]
    assessment: str
    overconfidence: bool
    underconfidence: bool
    balanced: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "buckets": self.buckets,
            "assessment": self.assessment,
            "overconfidence": self.overconfidence,
            "underconfidence": self.underconfidence,
            "balanced": self.balanced,
            "research_only": True,
        }
