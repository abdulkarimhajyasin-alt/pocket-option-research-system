"""Deterministic read-only external feed simulator."""

from __future__ import annotations

import random
from collections import deque
from datetime import UTC, datetime, timedelta

from loguru import logger

from app.external_data.base_feed import BaseExternalFeed
from app.external_data.feed_errors import FeedConfigurationError
from app.external_data.models import ExternalDataPayload, FeedSnapshot, FeedStatus
from app.external_data.monitor import ExternalFeedMonitor
from app.external_data.normalizer import FeedNormalizer


class SimulatedExternalFeed(BaseExternalFeed):
    """Simulate realistic external market data feeds without network or execution access."""

    def __init__(
        self,
        source: str = "simulated_external",
        symbol: str = "EURUSD",
        timeframe: str = "1m",
        latency_ms: float = 75.0,
        seed: int | None = 12,
        start_time: datetime | None = None,
        missing_every: int = 0,
        duplicate_every: int = 0,
        stale_every: int = 0,
        reconnect_every: int = 0,
    ) -> None:
        self.source = source
        self.normalizer = FeedNormalizer()
        self.symbol = self.normalizer.normalize_symbol(symbol)
        self.timeframe = self.normalizer.normalize_timeframe(timeframe)
        self.latency_ms = latency_ms
        self.random = random.Random(seed)
        self.current_time = start_time or datetime(2024, 1, 1, tzinfo=UTC)
        self.price = 1.1000
        self.sequence = 0
        self.missing_every = missing_every
        self.duplicate_every = duplicate_every
        self.stale_every = stale_every
        self.reconnect_every = reconnect_every
        self.subscriptions: set[tuple[str, str]] = set()
        self.status = FeedStatus.STOPPED
        self.monitor = ExternalFeedMonitor(source)
        self._pending: deque[ExternalDataPayload] = deque()

    def start(self) -> None:
        """Start local feed simulation."""
        self.validate_environment()
        self.status = FeedStatus.RUNNING
        self.monitor.start()
        logger.bind(component="external_data").info("External feed started {}", self.source)

    def stop(self) -> None:
        """Stop local feed simulation."""
        self.status = FeedStatus.STOPPED
        self.monitor.stop()
        logger.bind(component="external_data").info("External feed stopped {}", self.source)

    def is_running(self) -> bool:
        """Return True when feed generation is active."""
        return self.status in {FeedStatus.RUNNING, FeedStatus.DEGRADED, FeedStatus.RECONNECTING}

    def subscribe(self, symbol: str, timeframe: str) -> None:
        """Subscribe to a read-only simulated symbol/timeframe."""
        normalized_symbol = self.normalizer.normalize_symbol(symbol)
        normalized_timeframe = self.normalizer.normalize_timeframe(timeframe)
        self.subscriptions.add((normalized_symbol, normalized_timeframe))

    def unsubscribe(self, symbol: str, timeframe: str) -> None:
        """Remove a read-only simulated subscription."""
        self.subscriptions.discard(
            (
                self.normalizer.normalize_symbol(symbol),
                self.normalizer.normalize_timeframe(timeframe),
            )
        )

    def next_payload(self) -> ExternalDataPayload | None:
        """Return the next normalized simulated payload."""
        if not self.is_running():
            return None
        if self._pending:
            return self._record(self._pending.popleft())
        self._generate_candle()
        if not self._pending:
            return None
        return self._record(self._pending.popleft())

    def get_snapshot(self) -> FeedSnapshot:
        """Return simulator health and quality diagnostics."""
        symbols = tuple(sorted({symbol for symbol, _ in self.subscriptions} or {self.symbol}))
        timeframes = tuple(
            sorted({timeframe for _, timeframe in self.subscriptions} or {self.timeframe})
        )
        snapshot = self.monitor.snapshot(symbols, timeframes)
        return FeedSnapshot(
            source=snapshot.source,
            status=self.status if self.status != FeedStatus.RUNNING else snapshot.status,
            running=self.is_running(),
            symbols=snapshot.symbols,
            timeframes=snapshot.timeframes,
            last_event_at=snapshot.last_event_at,
            uptime_seconds=snapshot.uptime_seconds,
            reconnect_attempts=snapshot.reconnect_attempts,
            latency=snapshot.latency,
            quality=snapshot.quality,
            message=snapshot.message,
        )

    def validate_environment(self) -> None:
        """Validate local-only simulation settings."""
        if self.latency_ms < 0:
            raise FeedConfigurationError("latency_ms cannot be negative")
        for name, value in (
            ("missing_every", self.missing_every),
            ("duplicate_every", self.duplicate_every),
            ("stale_every", self.stale_every),
            ("reconnect_every", self.reconnect_every),
        ):
            if value < 0:
                raise FeedConfigurationError(f"{name} cannot be negative")

    def simulate_reconnect(self) -> None:
        """Simulate a read-only reconnect cycle."""
        self.monitor.record_reconnect()
        self.status = FeedStatus.RUNNING

    def _generate_candle(self) -> None:
        self.sequence += 1
        if self.reconnect_every and self.sequence % self.reconnect_every == 0:
            self.simulate_reconnect()
        if self.missing_every and self.sequence % self.missing_every == 0:
            self.current_time += timedelta(minutes=2)
            return
        self.current_time += timedelta(minutes=1)
        drift = self.random.gauss(0.0, 0.00008)
        open_price = self.price
        close_price = max(0.0001, open_price + drift)
        high = max(open_price, close_price) + abs(self.random.gauss(0.0, 0.00003))
        low = min(open_price, close_price) - abs(self.random.gauss(0.0, 0.00003))
        self.price = close_price
        timestamp = self.current_time
        if self.stale_every and self.sequence % self.stale_every == 0:
            timestamp -= timedelta(minutes=10)
        payload = self.normalizer.normalize_candle(
            {
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "timestamp": timestamp,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close_price,
                "volume": 100 + self.sequence,
                "latency_ms": self.latency_ms,
                "sequence": self.sequence,
                "is_closed": True,
            },
            source=self.source,
            sequence=self.sequence,
        )
        self._pending.append(payload)
        if self.duplicate_every and self.sequence % self.duplicate_every == 0:
            self._pending.append(payload)

    def _record(self, payload: ExternalDataPayload) -> ExternalDataPayload:
        self.monitor.record_payload(payload)
        logger.bind(component="external_data").debug("External feed payload {}", payload.to_dict())
        return payload
