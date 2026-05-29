"""Health snapshots for read-only stream services."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.streaming.models import StreamMetrics, StreamStatus


@dataclass(frozen=True)
class StreamHealthSnapshot:
    """Point-in-time health diagnostics for a market stream."""

    status: StreamStatus
    running: bool
    source: str
    subscriptions: tuple[tuple[str, str], ...]
    last_event_at: datetime | None
    event_rate_per_second: float = 0.0
    average_latency_ms: float = 0.0
    stale_duration_seconds: float = 0.0
    dropped_events: int = 0
    validation_failures: int = 0
    reconnect_ready: bool = True
    message: str = "ok"

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable health snapshot."""
        return {
            "status": self.status.value,
            "running": self.running,
            "source": self.source,
            "subscriptions": [f"{symbol}:{timeframe}" for symbol, timeframe in self.subscriptions],
            "last_event_at": self.last_event_at.isoformat() if self.last_event_at else None,
            "event_rate_per_second": round(self.event_rate_per_second, 4),
            "average_latency_ms": round(self.average_latency_ms, 4),
            "stale_duration_seconds": round(self.stale_duration_seconds, 4),
            "dropped_events": self.dropped_events,
            "validation_failures": self.validation_failures,
            "reconnect_ready": self.reconnect_ready,
            "message": self.message,
        }


def build_stream_health(
    source: str,
    status: StreamStatus,
    subscriptions: set[tuple[str, str]],
    last_event_at: datetime | None,
    metrics: StreamMetrics,
    event_rate_per_second: float = 0.0,
    stale_duration_seconds: float = 0.0,
    message: str = "ok",
) -> StreamHealthSnapshot:
    """Build a standard health snapshot from stream state and metrics."""
    return StreamHealthSnapshot(
        status=status,
        running=status == StreamStatus.RUNNING,
        source=source,
        subscriptions=tuple(sorted(subscriptions)),
        last_event_at=last_event_at,
        event_rate_per_second=event_rate_per_second,
        average_latency_ms=metrics.average_latency_ms,
        stale_duration_seconds=stale_duration_seconds,
        dropped_events=metrics.dropped_events,
        validation_failures=metrics.validation_failures,
        reconnect_ready=status in {StreamStatus.STOPPED, StreamStatus.FAILED},
        message=message,
    )
