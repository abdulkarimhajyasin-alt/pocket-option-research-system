"""Read-only base contracts for external market data feeds."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.external_data.models import ExternalDataPayload, FeedEventType, FeedSnapshot, FeedStatus
from app.streaming.base_stream import BaseMarketStream
from app.streaming.health import StreamHealthSnapshot
from app.streaming.models import (
    CandleUpdate,
    MarketDataEvent,
    MarketTick,
    StreamEventType,
    StreamStatus,
)


class BaseExternalFeed(ABC):
    """Abstract read-only external market data feed.

    Feed implementations expose data only. The contract intentionally has no
    methods for order placement, browser automation, credentials, or execution.
    """

    source: str

    @abstractmethod
    def start(self) -> None:
        """Start read-only feed collection."""

    @abstractmethod
    def stop(self) -> None:
        """Stop read-only feed collection."""

    @abstractmethod
    def is_running(self) -> bool:
        """Return True when the feed is active."""

    @abstractmethod
    def subscribe(self, symbol: str, timeframe: str) -> None:
        """Subscribe to a data-only symbol/timeframe flow."""

    @abstractmethod
    def unsubscribe(self, symbol: str, timeframe: str) -> None:
        """Remove a data-only subscription."""

    @abstractmethod
    def next_payload(self) -> ExternalDataPayload | None:
        """Return the next normalized external data payload, if available."""

    @abstractmethod
    def get_snapshot(self) -> FeedSnapshot:
        """Return feed health and quality diagnostics."""

    @abstractmethod
    def validate_environment(self) -> None:
        """Validate local research prerequisites."""


class ExternalFeedStreamAdapter(BaseMarketStream):
    """Adapt a normalized external feed to the existing streaming engine."""

    def __init__(self, feed: BaseExternalFeed) -> None:
        self.feed = feed
        self.source = feed.source

    def start(self) -> None:
        """Start the wrapped read-only feed."""
        self.feed.start()

    def stop(self) -> None:
        """Stop the wrapped read-only feed."""
        self.feed.stop()

    def is_running(self) -> bool:
        """Return True when the wrapped feed is running."""
        return self.feed.is_running()

    def get_health(self) -> StreamHealthSnapshot:
        """Map external feed diagnostics onto stream health diagnostics."""
        snapshot = self.feed.get_snapshot()
        status = StreamStatus.RUNNING if snapshot.running else StreamStatus.STOPPED
        if snapshot.status == FeedStatus.FAILED:
            status = StreamStatus.FAILED
        return StreamHealthSnapshot(
            status=status,
            running=snapshot.running,
            source=snapshot.source,
            subscriptions=tuple(
                (symbol, timeframe)
                for symbol in snapshot.symbols
                for timeframe in snapshot.timeframes
            ),
            last_event_at=snapshot.last_event_at,
            average_latency_ms=snapshot.latency.average_ms,
            stale_duration_seconds=0.0,
            dropped_events=snapshot.quality.missing_count,
            validation_failures=snapshot.quality.ordering_issue_count,
            reconnect_ready=not snapshot.running,
            message=snapshot.message,
        )

    def subscribe(self, symbol: str, timeframe: str) -> None:
        """Subscribe through the wrapped feed."""
        self.feed.subscribe(symbol, timeframe)

    def unsubscribe(self, symbol: str, timeframe: str) -> None:
        """Unsubscribe through the wrapped feed."""
        self.feed.unsubscribe(symbol, timeframe)

    def next_event(self) -> MarketDataEvent | None:
        """Convert the next normalized payload into a stream event."""
        payload = self.feed.next_payload()
        if payload is None:
            return None
        if hasattr(payload, "timeframe"):
            candle = CandleUpdate(
                symbol=payload.symbol,
                timeframe=payload.timeframe,  # type: ignore[attr-defined]
                timestamp=payload.timestamp,
                open=payload.open,  # type: ignore[attr-defined]
                high=payload.high,  # type: ignore[attr-defined]
                low=payload.low,  # type: ignore[attr-defined]
                close=payload.close,  # type: ignore[attr-defined]
                source=payload.source,
                volume=payload.volume,
                is_closed=payload.is_closed,  # type: ignore[attr-defined]
                latency_ms=payload.latency_ms,
                sequence=payload.sequence,
            )
            return MarketDataEvent(
                StreamEventType.CANDLE,
                payload.symbol,
                payload.timestamp,
                payload.source,
                payload.sequence,
                candle=candle,
                latency_ms=payload.latency_ms,
            )
        tick = MarketTick(
            symbol=payload.symbol,
            timestamp=payload.timestamp,
            price=payload.price,  # type: ignore[attr-defined]
            source=payload.source,
            bid=payload.bid,  # type: ignore[attr-defined]
            ask=payload.ask,  # type: ignore[attr-defined]
            latency_ms=payload.latency_ms,
            sequence=payload.sequence,
        )
        return MarketDataEvent(
            StreamEventType.TICK,
            payload.symbol,
            payload.timestamp,
            payload.source,
            payload.sequence,
            tick=tick,
            latency_ms=payload.latency_ms,
        )

    def validate_environment(self) -> None:
        """Validate the wrapped feed."""
        self.feed.validate_environment()


class FeedContract:
    """Reusable contract metadata for feed registration."""

    def __init__(
        self,
        name: str,
        event_types: tuple[FeedEventType, ...] = (FeedEventType.TICK, FeedEventType.CANDLE),
        read_only: bool = True,
        broker_agnostic: bool = True,
    ) -> None:
        self.name = name
        self.event_types = event_types
        self.read_only = read_only
        self.broker_agnostic = broker_agnostic

    def validate(self) -> None:
        """Validate the feed contract remains research-only."""
        if not self.read_only:
            raise ValueError("External feed contracts must be read-only")
        if not self.broker_agnostic:
            raise ValueError("External feed contracts must be broker-agnostic")
