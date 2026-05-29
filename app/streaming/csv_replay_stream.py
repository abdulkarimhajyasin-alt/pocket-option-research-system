"""Replay historical CSV candles as read-only stream events."""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from app.data.csv_loader import CsvCandleLoader
from app.data.models import CandleSeries
from app.streaming.base_stream import BaseMarketStream
from app.streaming.health import StreamHealthSnapshot, build_stream_health
from app.streaming.models import (
    CandleUpdate,
    MarketDataEvent,
    StreamEventType,
    StreamMetrics,
    normalize_timeframe,
    utc_now,
)
from app.streaming.stream_state import StreamStateTracker


class CsvReplayMarketStream(BaseMarketStream):
    """Sequentially replay CSV candles as if they arrived in real time."""

    def __init__(
        self,
        csv_path: Path | str,
        symbol: str = "EURUSD",
        timeframe: str = "1m",
        speed_multiplier: float = 1.0,
        loader: CsvCandleLoader | None = None,
    ) -> None:
        self.source = "csv_replay_stream"
        self.csv_path = Path(csv_path)
        self.symbol = symbol.upper()
        self.timeframe = normalize_timeframe(timeframe)
        self.speed_multiplier = speed_multiplier
        self.loader = loader or CsvCandleLoader()
        self.state_tracker = StreamStateTracker()
        self.metrics = StreamMetrics()
        self._series: CandleSeries | None = None
        self._index = 0
        self._paused = False

    def start(self) -> None:
        """Load CSV candles and start replay."""
        self.validate_environment()
        self._series = self.loader.load(self.csv_path, self.symbol, self.timeframe)
        self._validate_order(self._series)
        self._index = 0
        self.state_tracker.mark_started()
        logger.bind(component="streaming").info("CSV replay stream started {}", self.csv_path)

    def stop(self) -> None:
        """Stop replay."""
        self.state_tracker.mark_stopped()
        logger.bind(component="streaming").info("CSV replay stream stopped")

    def pause(self) -> None:
        """Pause replay without clearing state."""
        self._paused = True

    def resume(self) -> None:
        """Resume replay."""
        self._paused = False

    def is_running(self) -> bool:
        """Return True when replay is running."""
        return self.state_tracker.state.running and not self._paused

    def get_health(self) -> StreamHealthSnapshot:
        """Return replay stream health."""
        return build_stream_health(
            self.source,
            self.state_tracker.state.status,
            self.state_tracker.state.subscriptions,
            self.state_tracker.state.last_event_at,
            self.metrics,
            stale_duration_seconds=self.state_tracker.stale_seconds(utc_now()),
        )

    def subscribe(self, symbol: str, timeframe: str) -> None:
        """Subscribe to replayed candles."""
        self.state_tracker.subscribe(symbol, normalize_timeframe(timeframe))

    def unsubscribe(self, symbol: str, timeframe: str) -> None:
        """Remove a replay subscription."""
        self.state_tracker.unsubscribe(symbol, normalize_timeframe(timeframe))

    def next_event(self) -> MarketDataEvent | None:
        """Return the next replayed candle event."""
        if not self.is_running() or self._series is None or self._index >= len(self._series):
            return None
        candle = self._series[self._index]
        self._index += 1
        update = CandleUpdate(
            symbol=candle.symbol,
            timeframe=candle.timeframe,
            timestamp=candle.timestamp,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            source=self.source,
            volume=candle.volume,
            is_closed=True,
            latency_ms=0.0,
            sequence=self._index,
        )
        event = MarketDataEvent(
            event_type=StreamEventType.CANDLE,
            symbol=update.symbol,
            timestamp=update.timestamp,
            source=self.source,
            sequence=self._index,
            candle=update,
        )
        self.metrics.record_event(event)
        self.state_tracker.record_event(event)
        return event

    def validate_environment(self) -> None:
        """Validate CSV replay prerequisites."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Replay CSV not found: {self.csv_path}")
        if self.speed_multiplier <= 0:
            raise ValueError("speed_multiplier must be positive")

    def _validate_order(self, series: CandleSeries) -> None:
        seen = set()
        previous = None
        for candle in series:
            if candle.timestamp in seen:
                raise ValueError("CSV replay cannot contain duplicate candle timestamps")
            if previous is not None and candle.timestamp <= previous:
                raise ValueError("CSV replay candles must be strictly timestamp ordered")
            seen.add(candle.timestamp)
            previous = candle.timestamp
