"""Live feed provider contracts and deterministic mock streaming."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

from app.live_feed.models import CandleUpdate, FeedHealth, FeedSnapshot, TickData


class MarketFeedProvider(ABC):
    """Observation-only live market feed provider contract."""

    @abstractmethod
    def connect(self) -> bool:
        """Open provider resources without broker automation."""

    @abstractmethod
    def disconnect(self) -> bool:
        """Close provider resources."""

    @abstractmethod
    def subscribe(self, assets: list[str], timeframes: list[str]) -> bool:
        """Subscribe to observation streams."""

    @abstractmethod
    def unsubscribe(self, assets: list[str]) -> bool:
        """Unsubscribe from observation streams."""

    @abstractmethod
    def health_check(self) -> FeedHealth:
        """Return current feed health."""

    @abstractmethod
    def get_latest(self) -> FeedSnapshot:
        """Return latest provider snapshot."""


class MockLiveFeedProvider(MarketFeedProvider):
    """Deterministic provider that simulates live market updates."""

    def __init__(
        self,
        timestamp: datetime | None = None,
        source: str = "mock_live_feed_provider",
    ) -> None:
        self.timestamp = timestamp or datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
        self.source = source
        self.connected = False
        self.assets = ["EURUSD", "GBPUSD", "USDJPY"]
        self.timeframes = ["1m", "5m"]

    def connect(self) -> bool:
        self.connected = True
        return True

    def disconnect(self) -> bool:
        self.connected = False
        return True

    def subscribe(self, assets: list[str], timeframes: list[str]) -> bool:
        self.assets = list(dict.fromkeys(assets)) or self.assets
        self.timeframes = [
            timeframe for timeframe in dict.fromkeys(timeframes) if timeframe in _SUPPORTED
        ] or self.timeframes
        return True

    def unsubscribe(self, assets: list[str]) -> bool:
        blocked = set(assets)
        self.assets = [asset for asset in self.assets if asset not in blocked]
        return True

    def health_check(self) -> FeedHealth:
        return FeedHealth(
            timestamp=self.timestamp,
            source=self.source,
            asset="ALL",
            timeframe="stream",
            metadata={"provider_mode": "mock", "research_only": True},
            score=88.0 if self.connected else 72.0,
            label="ممتاز" if self.connected else "جيد",
            stale_updates=0,
            missing_updates=0,
        )

    def get_latest(self) -> FeedSnapshot:
        ticks = tuple(self._ticks())
        candles = tuple(self._candles())
        return FeedSnapshot(
            timestamp=self.timestamp,
            source=self.source,
            asset="ALL",
            timeframe="stream",
            metadata={
                "provider_mode": "mock",
                "research_only": True,
                "observation_only": True,
                "no_broker_connection": True,
            },
            ticks=ticks,
            candles=candles,
            health=self.health_check(),
        )

    def _ticks(self) -> list[TickData]:
        ticks = []
        for asset_index, asset in enumerate(self.assets):
            for step in range(8):
                timestamp = self.timestamp - timedelta(seconds=(7 - step) * 5)
                price = round(1.08 + asset_index * 0.012 + step * 0.00008, 5)
                ticks.append(
                    TickData(
                        timestamp=timestamp,
                        source=self.source,
                        asset=asset,
                        timeframe="tick",
                        metadata={"sequence": step, "provider_mode": "mock"},
                        bid=round(price - 0.00005, 5),
                        ask=round(price + 0.00005, 5),
                        price=price,
                        volume=100 + asset_index * 20 + step,
                    )
                )
        return ticks

    def _candles(self) -> list[CandleUpdate]:
        candles = []
        for asset_index, asset in enumerate(self.assets):
            for timeframe in self.timeframes:
                for step in range(5):
                    timestamp = self.timestamp - timedelta(minutes=4 - step)
                    open_price = round(1.08 + asset_index * 0.012 + step * 0.00012, 5)
                    close_price = round(open_price + ((step % 3) - 1) * 0.0001, 5)
                    candles.append(
                        CandleUpdate(
                            timestamp=timestamp,
                            source=self.source,
                            asset=asset,
                            timeframe=timeframe,
                            metadata={"sequence": step, "provider_mode": "mock"},
                            open=open_price,
                            high=round(max(open_price, close_price) + 0.0002, 5),
                            low=round(min(open_price, close_price) - 0.0002, 5),
                            close=close_price,
                            volume=1000 + asset_index * 100 + step * 10,
                            is_closed=step < 4,
                        )
                    )
        return candles


_SUPPORTED = {"1m", "5m", "15m", "1h"}
