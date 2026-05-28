"""Backtesting result models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class TradeOutcome(StrEnum):
    """Supported backtest trade outcomes."""

    WIN = "win"
    LOSS = "loss"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class BacktestTrade:
    """Represents one simulated trade in a backtest."""

    symbol: str
    timeframe: str
    direction: str
    strategy_name: str
    confidence: float
    entry_timestamp: datetime
    entry_price: float
    exit_timestamp: datetime | None
    exit_price: float | None
    outcome: TradeOutcome
    pnl: float
    reason: str | None = None
    risk_rule: str | None = None


@dataclass(frozen=True)
class EquityPoint:
    """Represents an equity curve point after a simulated trade."""

    timestamp: datetime
    equity: float
    pnl: float


@dataclass
class BacktestResult:
    """Container for trades, equity curve, and generated metrics."""

    symbol: str
    timeframe: str
    strategy_name: str
    trades: list[BacktestTrade] = field(default_factory=list)
    equity_curve: list[EquityPoint] = field(default_factory=list)
    metrics: dict[str, float | int] = field(default_factory=dict)
    risk_summary: dict[str, object] = field(default_factory=dict)
    analytics_snapshot: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, float | int | str]:
        """Return a compact structured summary for display and reports."""
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "strategy_name": self.strategy_name,
            **self.metrics,
        }
