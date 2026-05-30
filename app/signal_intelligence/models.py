"""Typed signal intelligence models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from app.data.models import Candle


class ResearchSignalClass(str, Enum):
    """Research classification only, never an execution instruction."""

    CALL = "call"
    PUT = "put"
    NO_TRADE = "no_trade"


@dataclass(frozen=True)
class StructureState:
    timestamp: datetime
    asset: str
    timeframe: str
    pattern: str
    state: str
    points: dict[str, float]
    confidence_contribution: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "pattern": self.pattern,
            "state": self.state,
            "points": self.points,
            "confidence_contribution": self.confidence_contribution,
        }


@dataclass(frozen=True)
class CISDState:
    timestamp: datetime
    asset: str
    timeframe: str
    direction: str
    validated: bool
    confidence_contribution: float
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "direction": self.direction,
            "validated": self.validated,
            "confidence_contribution": self.confidence_contribution,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class FVGState:
    timestamp: datetime
    asset: str
    timeframe: str
    direction: str
    gap_size: float
    mitigated: bool
    freshness_score: float
    distance_from_price: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "direction": self.direction,
            "gap_size": self.gap_size,
            "mitigated": self.mitigated,
            "freshness_score": self.freshness_score,
            "distance_from_price": self.distance_from_price,
        }


@dataclass(frozen=True)
class IFVGState:
    timestamp: datetime
    asset: str
    timeframe: str
    origin_direction: str
    inverted: bool
    confirmed: bool
    confidence_contribution: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "origin_direction": self.origin_direction,
            "inverted": self.inverted,
            "confirmed": self.confirmed,
            "confidence_contribution": self.confidence_contribution,
        }


@dataclass(frozen=True)
class LiquidityState:
    timestamp: datetime
    asset: str
    timeframe: str
    local_high: float
    local_low: float
    sweep_direction: str
    sweep_confirmed: bool
    confidence_contribution: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "local_high": self.local_high,
            "local_low": self.local_low,
            "sweep_direction": self.sweep_direction,
            "sweep_confirmed": self.sweep_confirmed,
            "confidence_contribution": self.confidence_contribution,
        }


@dataclass(frozen=True)
class SessionState:
    timestamp: datetime
    asset: str
    timeframe: str
    session_name: str
    quality_score: float
    activity_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "session_name": self.session_name,
            "quality_score": self.quality_score,
            "activity_score": self.activity_score,
        }


@dataclass(frozen=True)
class SignalConfidence:
    score: float
    classification: str
    weights: dict[str, float]
    contributions: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "classification": self.classification,
            "weights": self.weights,
            "contributions": self.contributions,
        }


@dataclass(frozen=True)
class SignalIntelligenceResult:
    timestamp: datetime
    asset: str
    timeframe: str
    classification: ResearchSignalClass
    confidence: SignalConfidence
    explanation: str
    supporting_factors: list[str]
    rejection_factors: list[str]
    structure: StructureState
    cisd: CISDState
    fvg: FVGState | None
    ifvg: IFVGState | None
    liquidity: LiquidityState
    session: SessionState
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "classification": self.classification.value,
            "classification_ar": self.classification_ar,
            "confidence": self.confidence.to_dict(),
            "explanation": self.explanation,
            "supporting_factors": self.supporting_factors,
            "rejection_factors": self.rejection_factors,
            "structure": self.structure.to_dict(),
            "cisd": self.cisd.to_dict(),
            "fvg": self.fvg.to_dict() if self.fvg else None,
            "ifvg": self.ifvg.to_dict() if self.ifvg else None,
            "liquidity": self.liquidity.to_dict(),
            "session": self.session.to_dict(),
            "metadata": self.metadata,
            "research_only": True,
        }

    @property
    def classification_ar(self) -> str:
        labels = {
            ResearchSignalClass.CALL: "تصنيف صعودي",
            ResearchSignalClass.PUT: "تصنيف هبوطي",
            ResearchSignalClass.NO_TRADE: "لا توجد فرصة بحثية",
        }
        return labels[self.classification]


@dataclass(frozen=True)
class SignalIntelligenceSnapshot:
    timestamp: datetime
    asset: str
    timeframe: str
    candles: tuple[Candle, ...]
    signals: tuple[SignalIntelligenceResult, ...]
    analytics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "signals": [signal.to_dict() for signal in self.signals],
            "analytics": self.analytics,
            "research_only": True,
        }
