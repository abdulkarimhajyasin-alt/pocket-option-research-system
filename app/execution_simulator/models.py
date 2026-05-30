"""Models for offline binary-options execution simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import uuid4

from app.signals.signal import SignalDirection


class BinaryOutcome(StrEnum):
    """Supported deterministic binary outcomes."""

    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class ExpiryDuration(StrEnum):
    """Allowed research expiry durations."""

    SECONDS_30 = "30s"
    MINUTES_1 = "1m"
    MINUTES_2 = "2m"
    MINUTES_3 = "3m"
    MINUTES_5 = "5m"

    @property
    def delta(self) -> timedelta:
        mapping = {
            ExpiryDuration.SECONDS_30: timedelta(seconds=30),
            ExpiryDuration.MINUTES_1: timedelta(minutes=1),
            ExpiryDuration.MINUTES_2: timedelta(minutes=2),
            ExpiryDuration.MINUTES_3: timedelta(minutes=3),
            ExpiryDuration.MINUTES_5: timedelta(minutes=5),
        }
        return mapping[self]


@dataclass(frozen=True)
class SimulatedOrder:
    """A local-only simulated order request."""

    order_id: str
    symbol: str
    timeframe: str
    direction: SignalDirection
    confidence: float
    requested_at: datetime
    expiry: ExpiryDuration
    stake: float
    payout_ratio: float
    strategy_name: str

    @classmethod
    def create(
        cls,
        symbol: str,
        timeframe: str,
        direction: SignalDirection,
        confidence: float,
        requested_at: datetime,
        strategy_name: str,
        expiry: ExpiryDuration = ExpiryDuration.MINUTES_1,
        stake: float = 1.0,
        payout_ratio: float = 0.80,
    ) -> "SimulatedOrder":
        """Create a simulated order with a generated id."""
        return cls(
            order_id=f"sim-{uuid4()}",
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            confidence=confidence,
            requested_at=requested_at,
            expiry=expiry,
            stake=stake,
            payout_ratio=payout_ratio,
            strategy_name=strategy_name,
        )


@dataclass(frozen=True)
class SimulatedPosition:
    """A simulated position opened from a local order."""

    order_id: str
    entry_time: datetime
    expiry_time: datetime
    entry_price: float
    direction: SignalDirection
    stake: float
    payout_ratio: float


@dataclass(frozen=True)
class SimulatedTrade:
    """One completed simulated binary-options trade."""

    trade_id: str
    order_id: str
    symbol: str
    timeframe: str
    direction: str
    strategy_name: str
    confidence: float
    entry_time: datetime
    expiry_time: datetime | None
    entry_price: float
    expiry_price: float | None
    outcome: BinaryOutcome
    payout: float
    profit_loss: float
    expected_return: float
    actual_return: float
    blocked_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-safe trade data."""
        return {
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "direction": self.direction,
            "strategy_name": self.strategy_name,
            "confidence": self.confidence,
            "entry_time": self.entry_time.isoformat(),
            "expiry_time": self.expiry_time.isoformat() if self.expiry_time else None,
            "entry_price": self.entry_price,
            "expiry_price": self.expiry_price,
            "outcome": self.outcome.value,
            "payout": self.payout,
            "profit_loss": self.profit_loss,
            "expected_return": self.expected_return,
            "actual_return": self.actual_return,
            "blocked_reason": self.blocked_reason,
        }


@dataclass(frozen=True)
class SimulatedExecutionResult:
    """Full result from an execution simulation run."""

    trades: list[SimulatedTrade] = field(default_factory=list)
    analytics: dict[str, Any] = field(default_factory=dict)
    reports: dict[str, str] = field(default_factory=dict)
    readiness: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        """Return a compact result summary."""
        return {
            "total_trades": self.analytics.get("total_trades", 0),
            "wins": self.analytics.get("wins", 0),
            "losses": self.analytics.get("losses", 0),
            "blocked_trades": self.analytics.get("blocked_trades", 0),
            "win_rate": self.analytics.get("win_rate", 0.0),
            "profit_loss": self.analytics.get("profit_loss", 0.0),
            "reports": self.reports,
        }
