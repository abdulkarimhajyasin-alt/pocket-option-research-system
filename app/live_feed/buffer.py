"""Memory-safe rolling buffers for live-feed observations."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import DefaultDict

from app.live_feed.models import CandleUpdate, FeedSnapshot, TickData


class FeedBuffer:
    """Maintain bounded rolling tick and candle buffers."""

    supported_timeframes = {"1m", "5m", "15m", "1h"}

    def __init__(self, tick_retention: int = 500, candle_retention: int = 200) -> None:
        self.tick_retention = tick_retention
        self.candle_retention = candle_retention
        self._ticks: DefaultDict[str, deque[TickData]] = defaultdict(
            lambda: deque(maxlen=self.tick_retention)
        )
        self._candles: DefaultDict[tuple[str, str], deque[CandleUpdate]] = defaultdict(
            lambda: deque(maxlen=self.candle_retention)
        )
        self._snapshot: FeedSnapshot | None = None

    def add_tick(self, tick: TickData) -> None:
        """Add one tick to the rolling buffer."""
        self._ticks[tick.asset].append(tick)

    def add_candle(self, candle: CandleUpdate) -> None:
        """Add one candle update when its timeframe is supported."""
        if candle.timeframe not in self.supported_timeframes:
            raise ValueError(f"Unsupported live-feed timeframe: {candle.timeframe}")
        self._candles[(candle.asset, candle.timeframe)].append(candle)

    def update_snapshot(self, snapshot: FeedSnapshot) -> None:
        """Store latest snapshot and index contained updates."""
        self._snapshot = snapshot
        for tick in snapshot.ticks:
            self.add_tick(tick)
        for candle in snapshot.candles:
            self.add_candle(candle)

    def latest_snapshot(self) -> FeedSnapshot | None:
        """Return latest feed snapshot."""
        return self._snapshot

    def ticks(self, asset: str) -> list[TickData]:
        """Return buffered ticks for one asset."""
        return list(self._ticks.get(asset, ()))

    def candles(self, asset: str, timeframe: str) -> list[CandleUpdate]:
        """Return buffered candles for one asset/timeframe."""
        return list(self._candles.get((asset, timeframe), ()))

    def active_assets(self) -> list[str]:
        """Return assets with buffered updates."""
        assets = set(self._ticks)
        assets.update(asset for asset, _timeframe in self._candles)
        return sorted(assets)
