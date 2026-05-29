"""Typed models for explainable strategy research decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from app.data.models import Candle
from app.signals.signal import SignalDirection


class EvidenceDirection(StrEnum):
    """Directional meaning for one evidence item."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class SignalEvidence:
    """One explainable reason contributing to a strategy decision."""

    name: str
    direction: EvidenceDirection
    strength: float
    weight: float = 1.0
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Evidence name is required")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("Evidence strength must be between 0 and 1")
        if self.weight < 0:
            raise ValueError("Evidence weight cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        """Return serializable evidence."""
        row = asdict(self)
        row["direction"] = self.direction.value
        return row


@dataclass(frozen=True)
class StrategyRejection:
    """Structured reason a strategy did not emit a signal."""

    reason: str
    detail: str = ""
    severity: str = "info"

    def to_dict(self) -> dict[str, str]:
        """Return serializable rejection detail."""
        return asdict(self)


@dataclass(frozen=True)
class MarketContext:
    """Market state visible to research strategies."""

    candles: tuple[Candle, ...]
    latest_candle: Candle
    symbol: str
    timeframe: str
    session: str
    volatility_state: str = "unknown"
    trend_state: str = "neutral"
    detected_patterns: tuple[str, ...] = ()
    higher_timeframe: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a compact serializable market context without raw candle history."""
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.latest_candle.timestamp.isoformat(),
            "session": self.session,
            "volatility_state": self.volatility_state,
            "trend_state": self.trend_state,
            "detected_patterns": list(self.detected_patterns),
            "higher_timeframe": self.higher_timeframe,
            "history_length": len(self.candles),
        }


@dataclass(frozen=True)
class StrategyContext:
    """Full research context including evidence and rejections."""

    market: MarketContext
    evidence: tuple[SignalEvidence, ...] = ()
    rejections: tuple[StrategyRejection, ...] = ()

    def with_evidence(self, evidence: SignalEvidence) -> "StrategyContext":
        """Return a copy with one more evidence item."""
        return StrategyContext(
            market=self.market,
            evidence=(*self.evidence, evidence),
            rejections=self.rejections,
        )

    def with_rejection(self, rejection: StrategyRejection) -> "StrategyContext":
        """Return a copy with one more rejection."""
        return StrategyContext(
            market=self.market,
            evidence=self.evidence,
            rejections=(*self.rejections, rejection),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return serializable context details."""
        return {
            "market": self.market.to_dict(),
            "evidence": [item.to_dict() for item in self.evidence],
            "rejections": [item.to_dict() for item in self.rejections],
        }


@dataclass(frozen=True)
class StrategyDecision:
    """Final explainable decision from a research strategy."""

    strategy_name: str
    symbol: str
    timeframe: str
    timestamp: datetime
    direction: SignalDirection | None
    confidence: float
    generated_signal: bool
    evidence: tuple[SignalEvidence, ...] = ()
    rejections: tuple[StrategyRejection, ...] = ()
    bullish_score: float = 0.0
    bearish_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Return serializable strategy decision."""
        return {
            "strategy_name": self.strategy_name,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "direction": self.direction.value if self.direction else None,
            "confidence": round(self.confidence, 4),
            "generated_signal": self.generated_signal,
            "evidence": [item.to_dict() for item in self.evidence],
            "rejections": [item.to_dict() for item in self.rejections],
            "bullish_score": round(self.bullish_score, 4),
            "bearish_score": round(self.bearish_score, 4),
        }
