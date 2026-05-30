"""Typed live feed models for streaming market observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


def _validate_common(
    timestamp: datetime,
    source: str,
    asset: str,
    timeframe: str,
) -> None:
    if timestamp.tzinfo is None:
        raise ValueError("Feed timestamp must be timezone-aware")
    if not source.strip():
        raise ValueError("Feed source is required")
    if not asset.strip():
        raise ValueError("Feed asset is required")
    if not timeframe.strip():
        raise ValueError("Feed timeframe is required")


@dataclass(frozen=True)
class TickData:
    """One read-only market tick."""

    timestamp: datetime
    source: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    bid: float = 0.0
    ask: float = 0.0
    price: float = 0.0
    volume: float | None = None

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.source, self.asset, self.timeframe)
        if min(self.bid, self.ask, self.price) <= 0:
            raise ValueError("Tick prices must be positive")
        if self.ask < self.bid:
            raise ValueError("Tick ask must be greater than or equal to bid")
        if self.volume is not None and self.volume < 0:
            raise ValueError("Tick volume cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "bid": self.bid,
            "ask": self.ask,
            "price": self.price,
            "volume": self.volume,
        }


@dataclass(frozen=True)
class CandleUpdate:
    """One streaming candle update."""

    timestamp: datetime
    source: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float | None = None
    is_closed: bool = False

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.source, self.asset, self.timeframe)
        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("Candle prices must be positive")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("Candle high must be greater than or equal to OHLC prices")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("Candle low must be less than or equal to OHLC prices")
        if self.volume is not None and self.volume < 0:
            raise ValueError("Candle volume cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "is_closed": self.is_closed,
        }


@dataclass(frozen=True)
class FeedLatency:
    """Latency observation for one feed update."""

    timestamp: datetime
    source: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.source, self.asset, self.timeframe)
        if self.latency_ms < 0:
            raise ValueError("Feed latency cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "latency_ms": self.latency_ms,
        }


@dataclass(frozen=True)
class FeedHealth:
    """Deterministic feed health state."""

    timestamp: datetime
    source: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    label: str = "ضعيف"
    stale_updates: int = 0
    missing_updates: int = 0

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.source, self.asset, self.timeframe)
        if not 0 <= self.score <= 100:
            raise ValueError("Feed health score must be between 0 and 100")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "score": self.score,
            "label": self.label,
            "stale_updates": self.stale_updates,
            "missing_updates": self.missing_updates,
        }


@dataclass(frozen=True)
class FeedStatistics:
    """Aggregated feed metrics."""

    timestamp: datetime
    source: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    update_frequency: float = 0.0
    average_latency_ms: float = 0.0
    active_assets: int = 0
    uptime_seconds: float = 0.0
    missing_updates: int = 0
    health_score: float = 0.0

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.source, self.asset, self.timeframe)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "update_frequency": self.update_frequency,
            "average_latency_ms": self.average_latency_ms,
            "active_assets": self.active_assets,
            "uptime_seconds": self.uptime_seconds,
            "missing_updates": self.missing_updates,
            "health_score": self.health_score,
        }


@dataclass(frozen=True)
class FeedSnapshot:
    """Latest live-feed state for research dashboards."""

    timestamp: datetime
    source: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    ticks: tuple[TickData, ...] = ()
    candles: tuple[CandleUpdate, ...] = ()
    latencies: tuple[FeedLatency, ...] = ()
    statistics: FeedStatistics | None = None
    health: FeedHealth | None = None

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.source, self.asset, self.timeframe)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "ticks": [tick.to_dict() for tick in self.ticks],
            "candles": [candle.to_dict() for candle in self.candles],
            "latencies": [latency.to_dict() for latency in self.latencies],
            "statistics": self.statistics.to_dict() if self.statistics else None,
            "health": self.health.to_dict() if self.health else None,
        }
