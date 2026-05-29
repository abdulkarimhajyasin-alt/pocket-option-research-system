"""Deterministic local-only simulated market stream."""

from __future__ import annotations

import random
from collections import deque
from datetime import UTC, datetime, timedelta

from loguru import logger

from app.streaming.base_stream import BaseMarketStream
from app.streaming.candle_aggregator import CandleAggregator
from app.streaming.health import StreamHealthSnapshot, build_stream_health
from app.streaming.models import (
    MarketDataEvent,
    MarketTick,
    StreamEventType,
    StreamMetrics,
    normalize_timeframe,
    utc_now,
)
from app.streaming.stream_state import StreamStateTracker


class SimulatedMarketStream(BaseMarketStream):
    """Generate realistic read-only tick and candle events without network access."""

    def __init__(
        self,
        symbol: str = "EURUSD",
        timeframes: tuple[str, ...] = ("1m", "5m"),
        update_interval_seconds: float = 1.0,
        latency_ms: float = 25.0,
        seed: int | None = None,
        start_time: datetime | None = None,
    ) -> None:
        self.source = "simulated_stream"
        self.symbol = symbol.upper()
        self.timeframes = tuple(normalize_timeframe(timeframe) for timeframe in timeframes)
        self.update_interval_seconds = update_interval_seconds
        self.latency_ms = latency_ms
        self.random = random.Random(seed)
        self.current_time = start_time or datetime(2024, 1, 1, tzinfo=UTC)
        self.price = 1.1000
        self.sequence = 0
        self.state_tracker = StreamStateTracker()
        self.metrics = StreamMetrics()
        self.aggregators = {
            timeframe: CandleAggregator(timeframe, source=self.source)
            for timeframe in self.timeframes
        }
        self._pending: deque[MarketDataEvent] = deque()

    def start(self) -> None:
        """Start simulated local stream generation."""
        self.validate_environment()
        self.state_tracker.mark_started()
        logger.bind(component="streaming").info("Simulated stream started")

    def stop(self) -> None:
        """Stop simulated local stream generation."""
        self.state_tracker.mark_stopped()
        logger.bind(component="streaming").info("Simulated stream stopped")

    def is_running(self) -> bool:
        """Return True when the simulated stream is running."""
        return self.state_tracker.state.running

    def get_health(self) -> StreamHealthSnapshot:
        """Return simulated stream health."""
        return build_stream_health(
            self.source,
            self.state_tracker.state.status,
            self.state_tracker.state.subscriptions,
            self.state_tracker.state.last_event_at,
            self.metrics,
            stale_duration_seconds=self.state_tracker.stale_seconds(utc_now()),
        )

    def subscribe(self, symbol: str, timeframe: str) -> None:
        """Subscribe to a local simulated symbol/timeframe."""
        normalized = normalize_timeframe(timeframe)
        if symbol.upper() != self.symbol:
            raise ValueError("Simulated stream currently supports EURUSD sample symbol only")
        if normalized not in self.aggregators:
            self.aggregators[normalized] = CandleAggregator(normalized, source=self.source)
        self.state_tracker.subscribe(symbol, normalized)
        logger.bind(component="streaming").info(
            "Subscribed simulated stream {} {}",
            symbol,
            normalized,
        )

    def unsubscribe(self, symbol: str, timeframe: str) -> None:
        """Remove a simulated subscription."""
        self.state_tracker.unsubscribe(symbol, normalize_timeframe(timeframe))

    def next_event(self) -> MarketDataEvent | None:
        """Return the next deterministic simulated market event."""
        if not self.is_running():
            return None
        if self._pending:
            return self._record(self._pending.popleft())
        self._generate_tick_cycle()
        return self._record(self._pending.popleft()) if self._pending else None

    def validate_environment(self) -> None:
        """Validate safe local-only operation."""
        if self.update_interval_seconds <= 0:
            raise ValueError("update_interval_seconds must be positive")
        if self.latency_ms < 0:
            raise ValueError("latency_ms cannot be negative")

    def _generate_tick_cycle(self) -> None:
        self.sequence += 1
        self.current_time += timedelta(seconds=self.update_interval_seconds)
        spread = 0.00008
        drift = self.random.gauss(0.0, 0.00006)
        self.price = max(0.0001, self.price + drift)
        tick = MarketTick(
            symbol=self.symbol,
            timestamp=self.current_time,
            price=round(self.price, 5),
            source=self.source,
            bid=round(self.price - spread / 2, 5),
            ask=round(self.price + spread / 2, 5),
            latency_ms=self.latency_ms,
            sequence=self.sequence,
        )
        self._pending.append(self._event(StreamEventType.TICK, tick.timestamp, tick=tick))
        for symbol, timeframe in sorted(self.state_tracker.state.subscriptions):
            if symbol != self.symbol:
                continue
            for candle in self.aggregators[timeframe].update(tick):
                self._pending.append(
                    self._event(StreamEventType.CANDLE, candle.timestamp, candle=candle)
                )

    def _event(
        self,
        event_type: StreamEventType,
        timestamp: datetime,
        tick: MarketTick | None = None,
        candle: object | None = None,
    ) -> MarketDataEvent:
        return MarketDataEvent(
            event_type=event_type,
            symbol=self.symbol,
            timestamp=timestamp,
            source=self.source,
            sequence=self.sequence,
            tick=tick,
            candle=candle,  # type: ignore[arg-type]
            latency_ms=self.latency_ms,
        )

    def _record(self, event: MarketDataEvent) -> MarketDataEvent:
        self.metrics.record_event(event)
        self.state_tracker.record_event(event)
        logger.bind(component="streaming").debug("Emitted simulated event {}", event.to_dict())
        return event
