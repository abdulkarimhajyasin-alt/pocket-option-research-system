"""Analytics hooks for read-only stream processing."""

from dataclasses import dataclass

from app.streaming.models import StreamMetrics


@dataclass(frozen=True)
class StreamingAnalyticsSnapshot:
    """Compact stream analytics snapshot."""

    events_processed: int
    candles_emitted: int
    average_latency_ms: float
    validation_warnings: int
    dropped_events: int
    duplicate_events: int

    def to_dict(self) -> dict[str, float | int]:
        """Return serializable stream analytics."""
        return self.__dict__.copy()


class StreamingAnalytics:
    """Build stream analytics without controlling stream behavior."""

    def analyze(self, metrics: StreamMetrics) -> StreamingAnalyticsSnapshot:
        """Return a compact stream analytics snapshot."""
        return StreamingAnalyticsSnapshot(
            events_processed=metrics.events_processed,
            candles_emitted=metrics.candles_emitted,
            average_latency_ms=round(metrics.average_latency_ms, 4),
            validation_warnings=metrics.validation_warnings,
            dropped_events=metrics.dropped_events,
            duplicate_events=metrics.duplicate_events,
        )
