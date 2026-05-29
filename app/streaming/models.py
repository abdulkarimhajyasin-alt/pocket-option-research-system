"""Typed models for read-only market stream processing."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from app.data.models import Candle


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(tz=UTC)


class StreamEventType(str, Enum):
    """Supported read-only market stream event types."""

    TICK = "tick"
    CANDLE = "candle"
    HEARTBEAT = "heartbeat"
    STREAM_START = "stream_start"
    STREAM_STOP = "stream_stop"


class StreamStatus(str, Enum):
    """Lifecycle status for stream services."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    FAILED = "failed"


@dataclass(frozen=True)
class MarketTick:
    """One read-only market tick from a broker-agnostic source."""

    symbol: str
    timestamp: datetime
    price: float
    source: str = "local"
    bid: float | None = None
    ask: float | None = None
    latency_ms: float = 0.0
    sequence: int = 0

    def __post_init__(self) -> None:
        validate_symbol(self.symbol)
        validate_timestamp(self.timestamp)
        validate_price(self.price, "price")
        if self.bid is not None:
            validate_price(self.bid, "bid")
        if self.ask is not None:
            validate_price(self.ask, "ask")
        if self.bid is not None and self.ask is not None and self.bid > self.ask:
            raise ValueError("Tick bid cannot be greater than ask")
        if self.latency_ms < 0:
            raise ValueError("Tick latency cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable tick dictionary."""
        row = asdict(self)
        row["timestamp"] = self.timestamp.isoformat()
        return row


@dataclass(frozen=True)
class CandleUpdate:
    """Open or closed OHLC candle update emitted by a stream pipeline."""

    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    source: str = "local"
    volume: float | None = None
    is_closed: bool = False
    latency_ms: float = 0.0
    sequence: int = 0

    def __post_init__(self) -> None:
        validate_symbol(self.symbol)
        validate_timeframe(self.timeframe)
        validate_timestamp(self.timestamp)
        for name, value in (
            ("open", self.open),
            ("high", self.high),
            ("low", self.low),
            ("close", self.close),
        ):
            validate_price(value, name)
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("Candle high must be greater than or equal to OHLC prices")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("Candle low must be less than or equal to OHLC prices")
        if self.volume is not None and self.volume < 0:
            raise ValueError("Candle volume cannot be negative")
        if self.latency_ms < 0:
            raise ValueError("Candle latency cannot be negative")

    def to_candle(self) -> "Candle":
        """Convert this update to the core Candle model."""
        from app.data.models import Candle

        return Candle(
            symbol=self.symbol,
            timeframe=self.timeframe,
            timestamp=self.timestamp,
            open=self.open,
            high=self.high,
            low=self.low,
            close=self.close,
            volume=self.volume,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable candle update dictionary."""
        row = asdict(self)
        row["timestamp"] = self.timestamp.isoformat()
        return row


@dataclass(frozen=True)
class MarketDataEvent:
    """Envelope for read-only stream events."""

    event_type: StreamEventType
    symbol: str
    timestamp: datetime
    source: str
    sequence: int
    tick: MarketTick | None = None
    candle: CandleUpdate | None = None
    latency_ms: float = 0.0
    event_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        validate_symbol(self.symbol)
        validate_timestamp(self.timestamp)
        if self.sequence < 0:
            raise ValueError("Event sequence cannot be negative")
        if self.latency_ms < 0:
            raise ValueError("Event latency cannot be negative")
        if self.event_type == StreamEventType.TICK and self.tick is None:
            raise ValueError("Tick events require a MarketTick payload")
        if self.event_type == StreamEventType.CANDLE and self.candle is None:
            raise ValueError("Candle events require a CandleUpdate payload")

    @property
    def timeframe(self) -> str | None:
        """Return the candle timeframe when this event carries one."""
        return self.candle.timeframe if self.candle else None

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable event dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "sequence": self.sequence,
            "latency_ms": self.latency_ms,
            "tick": self.tick.to_dict() if self.tick else None,
            "candle": self.candle.to_dict() if self.candle else None,
        }


@dataclass(frozen=True)
class StreamBatch:
    """Small ordered batch of market stream events."""

    events: tuple[MarketDataEvent, ...]
    source: str
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        validate_timestamp(self.created_at)
        previous: tuple[datetime, int] | None = None
        for event in self.events:
            key = (event.timestamp, event.sequence)
            if previous is not None and key < previous:
                raise ValueError("StreamBatch events must be timestamp/sequence ordered")
            previous = key


@dataclass
class StreamState:
    """Mutable lifecycle state for a market stream."""

    status: StreamStatus = StreamStatus.STOPPED
    subscriptions: set[tuple[str, str]] = field(default_factory=set)
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    last_event_at: datetime | None = None
    last_sequence: int = -1
    error: str | None = None

    @property
    def running(self) -> bool:
        """Return True when the stream is actively running."""
        return self.status == StreamStatus.RUNNING

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable stream state snapshot."""
        return {
            "status": self.status.value,
            "subscriptions": sorted(
                f"{symbol}:{timeframe}" for symbol, timeframe in self.subscriptions
            ),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "last_event_at": self.last_event_at.isoformat() if self.last_event_at else None,
            "last_sequence": self.last_sequence,
            "error": self.error,
        }


@dataclass
class StreamMetrics:
    """Counters and latency samples for stream analytics."""

    events_processed: int = 0
    ticks_processed: int = 0
    candles_emitted: int = 0
    validation_warnings: int = 0
    validation_failures: int = 0
    dropped_events: int = 0
    duplicate_events: int = 0
    latency_samples_ms: list[float] = field(default_factory=list)

    @property
    def average_latency_ms(self) -> float:
        """Return average observed stream latency in milliseconds."""
        if not self.latency_samples_ms:
            return 0.0
        return sum(self.latency_samples_ms) / len(self.latency_samples_ms)

    def record_event(self, event: MarketDataEvent) -> None:
        """Update metrics for an accepted event."""
        self.events_processed += 1
        if event.event_type == StreamEventType.TICK:
            self.ticks_processed += 1
        elif event.event_type == StreamEventType.CANDLE:
            self.candles_emitted += 1
        self.latency_samples_ms.append(event.latency_ms)

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable metrics snapshot."""
        return {
            "events_processed": self.events_processed,
            "ticks_processed": self.ticks_processed,
            "candles_emitted": self.candles_emitted,
            "validation_warnings": self.validation_warnings,
            "validation_failures": self.validation_failures,
            "dropped_events": self.dropped_events,
            "duplicate_events": self.duplicate_events,
            "average_latency_ms": round(self.average_latency_ms, 4),
        }


def validate_symbol(symbol: str) -> None:
    """Validate a broker-agnostic market symbol."""
    if not symbol.strip():
        raise ValueError("Symbol is required")


def validate_timeframe(timeframe: str) -> None:
    """Validate supported streaming timeframe values."""
    if timeframe not in {"1m", "5m", "M1", "M5"}:
        raise ValueError("Streaming supports only M1/1m and M5/5m timeframes")


def normalize_timeframe(timeframe: str) -> str:
    """Normalize supported stream timeframes to core runtime style."""
    value = timeframe.strip()
    mapping = {"M1": "1m", "m1": "1m", "M5": "5m", "m5": "5m"}
    normalized = mapping.get(value, value)
    validate_timeframe(normalized)
    return normalized


def validate_timestamp(timestamp: datetime) -> None:
    """Validate a timezone-aware timestamp."""
    if timestamp.tzinfo is None:
        raise ValueError("Stream timestamps must be timezone-aware")


def validate_price(price: float, field_name: str = "price") -> None:
    """Validate a positive market price."""
    if price <= 0:
        raise ValueError(f"{field_name} must be positive")
