"""Analytics domain models for research workflows."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TradeJournalEntry:
    """Append-only trade lifecycle record used by runtime and backtesting."""

    trade_id: str
    lifecycle_state: str
    strategy_name: str
    symbol: str
    timeframe: str
    direction: str
    confidence: float
    timestamp: datetime
    pnl: float = 0.0
    balance: float | None = None
    outcome: str | None = None
    rejection_reason: str | None = None
    risk_rule: str | None = None
    entry_price: float | None = None
    exit_price: float | None = None
    runtime_mode: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        row = asdict(self)
        row["timestamp"] = self.timestamp.isoformat()
        return row


@dataclass(frozen=True)
class EquityCurvePoint:
    """Time-indexed account equity point."""

    timestamp: datetime
    equity: float
    cumulative_pnl: float
    drawdown: float
    peak: float
    trough: float

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        row = asdict(self)
        row["timestamp"] = self.timestamp.isoformat()
        return row


@dataclass(frozen=True)
class SessionPerformance:
    """Aggregated performance for one market session."""

    session_name: str
    trades: int
    wins: int
    losses: int
    pnl: float
    rejection_rate: float
    average_confidence: float


@dataclass(frozen=True)
class SymbolPerformance:
    """Aggregated performance for one symbol."""

    symbol: str
    trades: int
    wins: int
    losses: int
    pnl: float
    rejection_count: int
    average_confidence: float
    exposure_frequency: int


@dataclass(frozen=True)
class RuntimePerformance:
    """Runtime analytics snapshot."""

    uptime_seconds: float
    execution_throughput: float
    signals_per_hour: float
    runtime_errors: int
    blocked_signals: int
    settlement_latency: float
    processing_latency: float


@dataclass(frozen=True)
class AnalyticsSnapshot:
    """Structured analytics snapshot for research reports."""

    generated_at: datetime
    trade_count: int
    net_pnl: float
    max_drawdown: float
    strategy_performance: dict[str, dict[str, float | int]]
    symbol_performance: list[SymbolPerformance]
    session_performance: list[SessionPerformance]
    hourly_performance: dict[int, dict[str, float | int]]
    rejection_analysis: dict[str, int]
    streak_analysis: dict[str, int | float]
    exposure_analysis: dict[str, int]
    runtime_performance: RuntimePerformance | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        row = asdict(self)
        row["generated_at"] = self.generated_at.isoformat()
        return row
