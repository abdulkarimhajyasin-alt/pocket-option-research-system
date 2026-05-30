"""Typed models for research-only market data integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


def _validate_common(
    timestamp: datetime,
    provider: str,
    asset: str,
    timeframe: str,
) -> None:
    if timestamp.tzinfo is None:
        raise ValueError("Market data timestamp must be timezone-aware")
    if not provider.strip():
        raise ValueError("Market data provider is required")
    if not asset.strip():
        raise ValueError("Market data asset is required")
    if not timeframe.strip():
        raise ValueError("Market data timeframe is required")


@dataclass(frozen=True)
class MarketAsset:
    """Research asset available from a market-data provider."""

    timestamp: datetime
    provider: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    display_name: str | None = None
    asset_class: str = "forex"
    is_active: bool = True
    quality_score: float = 0.0

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.provider, self.asset, self.timeframe)
        if not 0 <= self.quality_score <= 100:
            raise ValueError("Asset quality score must be between 0 and 100")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "display_name": self.display_name or self.asset,
            "asset_class": self.asset_class,
            "is_active": self.is_active,
            "quality_score": self.quality_score,
        }


@dataclass(frozen=True)
class MarketCandle:
    """Provider candle normalized for research analytics."""

    timestamp: datetime
    provider: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float | None = None

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.provider, self.asset, self.timeframe)
        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("Market candle prices must be positive")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("Market candle high must be greater than or equal to OHLC")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("Market candle low must be less than or equal to OHLC")
        if self.volume is not None and self.volume < 0:
            raise ValueError("Market candle volume cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


@dataclass(frozen=True)
class MarketSession:
    """Observed market session activity."""

    timestamp: datetime
    provider: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    name: str = "asian"
    is_active: bool = False
    activity_score: float = 0.0

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.provider, self.asset, self.timeframe)
        if not self.name.strip():
            raise ValueError("Market session name is required")
        if not 0 <= self.activity_score <= 100:
            raise ValueError("Session activity score must be between 0 and 100")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "name": self.name,
            "is_active": self.is_active,
            "activity_score": self.activity_score,
        }


@dataclass(frozen=True)
class MarketStatus:
    """Provider market status for research visibility."""

    timestamp: datetime
    provider: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "open"
    coverage_score: float = 0.0
    update_frequency: float = 0.0

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.provider, self.asset, self.timeframe)
        if not 0 <= self.coverage_score <= 100:
            raise ValueError("Market coverage score must be between 0 and 100")
        if self.update_frequency < 0:
            raise ValueError("Market update frequency cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "status": self.status,
            "coverage_score": self.coverage_score,
            "update_frequency": self.update_frequency,
        }


@dataclass(frozen=True)
class MarketLatency:
    """Provider latency metric."""

    timestamp: datetime
    provider: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.provider, self.asset, self.timeframe)
        if self.latency_ms < 0:
            raise ValueError("Market latency cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "latency_ms": self.latency_ms,
        }


@dataclass(frozen=True)
class MarketDataHealth:
    """Research-only provider health state."""

    timestamp: datetime
    provider: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    label: str = "ضعيف"
    readiness_score: float = 0.0
    readiness_label: str = "غير جاهز"

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.provider, self.asset, self.timeframe)
        if not 0 <= self.score <= 100:
            raise ValueError("Market health score must be between 0 and 100")
        if not 0 <= self.readiness_score <= 100:
            raise ValueError("Readiness score must be between 0 and 100")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "score": self.score,
            "label": self.label,
            "readiness_score": self.readiness_score,
            "readiness_label": self.readiness_label,
        }


@dataclass(frozen=True)
class MarketProviderInfo:
    """Provider metadata used by provider switching architecture."""

    name: str
    provider_type: str
    supports_realtime: bool
    supports_historical: bool
    research_only: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "provider_type": self.provider_type,
            "supports_realtime": self.supports_realtime,
            "supports_historical": self.supports_historical,
            "research_only": self.research_only,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class MarketSnapshot:
    """Complete provider snapshot consumed by dashboards and research services."""

    timestamp: datetime
    provider: str
    asset: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
    provider_info: MarketProviderInfo | None = None
    assets: tuple[MarketAsset, ...] = ()
    candles: tuple[MarketCandle, ...] = ()
    sessions: tuple[MarketSession, ...] = ()
    statuses: tuple[MarketStatus, ...] = ()
    latencies: tuple[MarketLatency, ...] = ()
    health: MarketDataHealth | None = None

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.provider, self.asset, self.timeframe)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "asset": self.asset,
            "timeframe": self.timeframe,
            "metadata": self.metadata,
            "provider_info": self.provider_info.to_dict() if self.provider_info else None,
            "assets": [item.to_dict() for item in self.assets],
            "candles": [item.to_dict() for item in self.candles],
            "sessions": [item.to_dict() for item in self.sessions],
            "statuses": [item.to_dict() for item in self.statuses],
            "latencies": [item.to_dict() for item in self.latencies],
            "health": self.health.to_dict() if self.health else None,
        }
