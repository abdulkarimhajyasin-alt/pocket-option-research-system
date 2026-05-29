"""Runtime monitoring for read-only market streams."""

from datetime import datetime

from app.streaming.health import StreamHealthSnapshot
from app.streaming.models import MarketDataEvent, StreamMetrics, StreamStatus, utc_now


class StreamMonitor:
    """Track event rate, latency, dropped events, and reconnect readiness."""

    def __init__(self, source: str, stale_after_seconds: float = 120.0) -> None:
        self.source = source
        self.stale_after_seconds = stale_after_seconds
        self.metrics = StreamMetrics()
        self.started_at: datetime | None = None
        self.last_event_at: datetime | None = None
        self.running = False

    def start(self) -> None:
        """Mark monitoring as running."""
        self.started_at = utc_now()
        self.running = True

    def stop(self) -> None:
        """Mark monitoring as stopped."""
        self.running = False

    def record_event(self, event: MarketDataEvent) -> None:
        """Record a processed stream event."""
        self.metrics.record_event(event)
        self.last_event_at = event.timestamp

    def record_validation(self, warnings: int = 0, failures: int = 0) -> None:
        """Record validation outcomes."""
        self.metrics.validation_warnings += warnings
        self.metrics.validation_failures += failures

    def record_drop(self, duplicate: bool = False) -> None:
        """Record a dropped event."""
        self.metrics.dropped_events += 1
        if duplicate:
            self.metrics.duplicate_events += 1

    def snapshot(self, subscriptions: set[tuple[str, str]] | None = None) -> StreamHealthSnapshot:
        """Return a health snapshot."""
        now = utc_now()
        uptime = (now - self.started_at).total_seconds() if self.started_at else 0.0
        stale = (now - self.last_event_at).total_seconds() if self.last_event_at else 0.0
        status = StreamStatus.RUNNING if self.running else StreamStatus.STOPPED
        message = "stale data" if stale > self.stale_after_seconds else "ok"
        return StreamHealthSnapshot(
            status=status,
            running=self.running,
            source=self.source,
            subscriptions=tuple(sorted(subscriptions or set())),
            last_event_at=self.last_event_at,
            event_rate_per_second=(self.metrics.events_processed / uptime) if uptime else 0.0,
            average_latency_ms=self.metrics.average_latency_ms,
            stale_duration_seconds=stale,
            dropped_events=self.metrics.dropped_events,
            validation_failures=self.metrics.validation_failures,
            reconnect_ready=not self.running,
            message=message,
        )
