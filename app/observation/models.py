"""Typed models for broker observation research data."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


def _validate_common(
    timestamp: datetime,
    asset: str,
    timeframe: str,
    source: str,
) -> None:
    if timestamp.tzinfo is None:
        raise ValueError("Observation timestamp must be timezone-aware")
    if not asset.strip():
        raise ValueError("Observation asset is required")
    if not timeframe.strip():
        raise ValueError("Observation timeframe is required")
    if not source.strip():
        raise ValueError("Observation source is required")


@dataclass(frozen=True)
class AssetObservation:
    """Observed availability and activity for one market asset."""

    timestamp: datetime
    asset: str
    timeframe: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    activity_score: float = 0.0
    display_name: str | None = None

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.asset, self.timeframe, self.source)
        if not 0 <= self.activity_score <= 100:
            raise ValueError("Asset activity score must be between 0 and 100")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "source": self.source,
            "metadata": self.metadata,
            "is_active": self.is_active,
            "activity_score": self.activity_score,
            "display_name": self.display_name or self.asset,
        }


@dataclass(frozen=True)
class MarketObservation:
    """Observed market visibility for one asset."""

    timestamp: datetime
    asset: str
    timeframe: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    spread_proxy: float = 0.0
    volatility_score: float = 0.0

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.asset, self.timeframe, self.source)
        if self.spread_proxy < 0:
            raise ValueError("Spread proxy cannot be negative")
        if not 0 <= self.volatility_score <= 100:
            raise ValueError("Volatility score must be between 0 and 100")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "source": self.source,
            "metadata": self.metadata,
            "status": self.status,
            "spread_proxy": self.spread_proxy,
            "volatility_score": self.volatility_score,
        }


@dataclass(frozen=True)
class PayoutObservation:
    """Observed payout level for one asset."""

    timestamp: datetime
    asset: str
    timeframe: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    payout_percent: float = 0.0

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.asset, self.timeframe, self.source)
        if not 0 <= self.payout_percent <= 100:
            raise ValueError("Payout percent must be between 0 and 100")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "source": self.source,
            "metadata": self.metadata,
            "payout_percent": self.payout_percent,
        }


@dataclass(frozen=True)
class SessionObservation:
    """Observed session activity for a market session."""

    timestamp: datetime
    asset: str
    timeframe: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    session_name: str = "asian"
    is_active: bool = False
    activity_score: float = 0.0

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.asset, self.timeframe, self.source)
        if not self.session_name.strip():
            raise ValueError("Session name is required")
        if not 0 <= self.activity_score <= 100:
            raise ValueError("Session activity score must be between 0 and 100")

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "source": self.source,
            "metadata": self.metadata,
            "session_name": self.session_name,
            "is_active": self.is_active,
            "activity_score": self.activity_score,
        }


@dataclass(frozen=True)
class CandleObservation:
    """Read-only observed OHLC candle."""

    timestamp: datetime
    asset: str
    timeframe: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float | None = None

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.asset, self.timeframe, self.source)
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
            "asset": self.asset,
            "timeframe": self.timeframe,
            "source": self.source,
            "metadata": self.metadata,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


@dataclass(frozen=True)
class BrokerSnapshot:
    """Complete read-only snapshot from an observation provider."""

    timestamp: datetime
    asset: str
    timeframe: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    assets: tuple[AssetObservation, ...] = ()
    markets: tuple[MarketObservation, ...] = ()
    payouts: tuple[PayoutObservation, ...] = ()
    sessions: tuple[SessionObservation, ...] = ()
    candles: tuple[CandleObservation, ...] = ()

    def __post_init__(self) -> None:
        _validate_common(self.timestamp, self.asset, self.timeframe, self.source)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "asset": self.asset,
            "timeframe": self.timeframe,
            "source": self.source,
            "metadata": self.metadata,
            "assets": [item.to_dict() for item in self.assets],
            "markets": [item.to_dict() for item in self.markets],
            "payouts": [item.to_dict() for item in self.payouts],
            "sessions": [item.to_dict() for item in self.sessions],
            "candles": [item.to_dict() for item in self.candles],
        }
