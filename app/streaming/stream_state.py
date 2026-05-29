"""Helpers for maintaining stream lifecycle state."""

from datetime import datetime

from app.streaming.models import MarketDataEvent, StreamState, StreamStatus, utc_now


class StreamStateTracker:
    """Small lifecycle helper shared by stream implementations."""

    def __init__(self) -> None:
        self.state = StreamState()

    def mark_started(self) -> None:
        """Mark the stream as running."""
        self.state.status = StreamStatus.RUNNING
        self.state.started_at = utc_now()
        self.state.stopped_at = None
        self.state.error = None

    def mark_stopped(self) -> None:
        """Mark the stream as stopped."""
        self.state.status = StreamStatus.STOPPED
        self.state.stopped_at = utc_now()

    def mark_failed(self, error: str) -> None:
        """Mark the stream as failed."""
        self.state.status = StreamStatus.FAILED
        self.state.error = error
        self.state.stopped_at = utc_now()

    def record_event(self, event: MarketDataEvent) -> None:
        """Record latest event timing and sequence."""
        self.state.last_event_at = event.timestamp
        self.state.last_sequence = event.sequence

    def subscribe(self, symbol: str, timeframe: str) -> None:
        """Track a subscription."""
        self.state.subscriptions.add((symbol.upper(), timeframe))

    def unsubscribe(self, symbol: str, timeframe: str) -> None:
        """Remove a subscription if present."""
        self.state.subscriptions.discard((symbol.upper(), timeframe))

    def stale_seconds(self, now: datetime | None = None) -> float:
        """Return seconds since the last event."""
        if self.state.last_event_at is None:
            return 0.0
        current = now or utc_now()
        return max(0.0, (current - self.state.last_event_at).total_seconds())
