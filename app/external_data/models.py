"""Typed models for broker-agnostic external market data research."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(tz=UTC)


class FeedStatus(str, Enum):
    """Lifecycle state for read-only external feeds."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


class FeedEventType(str, Enum):
    """Supported read-only external feed payload types."""

    TICK = "tick"
    CANDLE = "candle"
    HEARTBEAT = "heartbeat"


@dataclass(frozen=True)
class NormalizedTick:
    """Source-independent market tick."""

    symbol: str
    timestamp: datetime
    price: float
    source: str
    bid: float | None = None
    ask: float | None = None
    volume: float | None = None
    latency_ms: float = 0.0
    sequence: int = 0
    received_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _validate_symbol(self.symbol)
        _validate_timestamp(self.timestamp)
        _validate_timestamp(self.received_at)
        _validate_price(self.price, "price")
        if self.bid is not None:
            _validate_price(self.bid, "bid")
        if self.ask is not None:
            _validate_price(self.ask, "ask")
        if self.bid is not None and self.ask is not None and self.bid > self.ask:
            raise ValueError("Tick bid cannot be greater than ask")
        _validate_non_negative(self.latency_ms, "latency_ms")
        if self.volume is not None:
            _validate_non_negative(self.volume, "volume")
        if self.sequence < 0:
            raise ValueError("sequence cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary."""
        row = asdict(self)
        row["timestamp"] = self.timestamp.isoformat()
        row["received_at"] = self.received_at.isoformat()
        return row


@dataclass(frozen=True)
class NormalizedCandle:
    """Source-independent OHLCV candle."""

    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    source: str
    volume: float | None = None
    is_closed: bool = True
    latency_ms: float = 0.0
    sequence: int = 0
    received_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _validate_symbol(self.symbol)
        _validate_symbol(self.timeframe)
        _validate_timestamp(self.timestamp)
        _validate_timestamp(self.received_at)
        for name, value in (
            ("open", self.open),
            ("high", self.high),
            ("low", self.low),
            ("close", self.close),
        ):
            _validate_price(value, name)
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("Candle high must be greater than or equal to OHLC prices")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("Candle low must be less than or equal to OHLC prices")
        if self.volume is not None:
            _validate_non_negative(self.volume, "volume")
        _validate_non_negative(self.latency_ms, "latency_ms")
        if self.sequence < 0:
            raise ValueError("sequence cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary."""
        row = asdict(self)
        row["timestamp"] = self.timestamp.isoformat()
        row["received_at"] = self.received_at.isoformat()
        return row


@dataclass(frozen=True)
class FeedLatencyMetrics:
    """Latency distribution for a feed sample."""

    sample_count: int = 0
    average_ms: float = 0.0
    maximum_ms: float = 0.0
    latest_ms: float = 0.0
    threshold_ms: float = 1_000.0

    @property
    def threshold_breached(self) -> bool:
        """Return True when latest or maximum latency exceeds the threshold."""
        return self.latest_ms > self.threshold_ms or self.maximum_ms > self.threshold_ms

    def to_dict(self) -> dict[str, float | int | bool]:
        """Return serializable latency metrics."""
        return {
            "sample_count": self.sample_count,
            "average_ms": round(self.average_ms, 4),
            "maximum_ms": round(self.maximum_ms, 4),
            "latest_ms": round(self.latest_ms, 4),
            "threshold_ms": round(self.threshold_ms, 4),
            "threshold_breached": self.threshold_breached,
        }


@dataclass(frozen=True)
class FeedQualityMetrics:
    """Quality diagnostics for normalized external feed data."""

    sample_count: int = 0
    stale_count: int = 0
    missing_count: int = 0
    duplicate_count: int = 0
    ordering_issue_count: int = 0
    gap_count: int = 0
    latency_warning_count: int = 0
    quality_score: float = 100.0
    issues: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        """Return serializable quality metrics."""
        return {
            "sample_count": self.sample_count,
            "stale_count": self.stale_count,
            "missing_count": self.missing_count,
            "duplicate_count": self.duplicate_count,
            "ordering_issue_count": self.ordering_issue_count,
            "gap_count": self.gap_count,
            "latency_warning_count": self.latency_warning_count,
            "quality_score": round(self.quality_score, 4),
            "issues": list(self.issues),
        }


@dataclass(frozen=True)
class FeedSnapshot:
    """Point-in-time external feed state."""

    source: str
    status: FeedStatus
    running: bool
    symbols: tuple[str, ...]
    timeframes: tuple[str, ...]
    last_event_at: datetime | None = None
    uptime_seconds: float = 0.0
    reconnect_attempts: int = 0
    latency: FeedLatencyMetrics = field(default_factory=FeedLatencyMetrics)
    quality: FeedQualityMetrics = field(default_factory=FeedQualityMetrics)
    message: str = "ok"
    captured_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, object]:
        """Return a serializable feed snapshot."""
        return {
            "source": self.source,
            "status": self.status.value,
            "running": self.running,
            "symbols": list(self.symbols),
            "timeframes": list(self.timeframes),
            "last_event_at": self.last_event_at.isoformat() if self.last_event_at else None,
            "uptime_seconds": round(self.uptime_seconds, 4),
            "reconnect_attempts": self.reconnect_attempts,
            "latency": self.latency.to_dict(),
            "quality": self.quality.to_dict(),
            "message": self.message,
            "captured_at": self.captured_at.isoformat(),
        }


ExternalDataPayload = NormalizedTick | NormalizedCandle


def _validate_symbol(value: str) -> None:
    if not value.strip():
        raise ValueError("value is required")


def _validate_timestamp(timestamp: datetime) -> None:
    if timestamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")


def _validate_price(value: float, field_name: str) -> None:
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _validate_non_negative(value: float, field_name: str) -> None:
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative")
