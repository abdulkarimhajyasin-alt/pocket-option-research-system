"""Health helpers for read-only external data feeds."""

from app.external_data.models import (
    FeedLatencyMetrics,
    FeedQualityMetrics,
    FeedSnapshot,
    FeedStatus,
)


def build_feed_snapshot(
    source: str,
    status: FeedStatus,
    symbols: tuple[str, ...],
    timeframes: tuple[str, ...],
    uptime_seconds: float = 0.0,
    reconnect_attempts: int = 0,
    latency: FeedLatencyMetrics | None = None,
    quality: FeedQualityMetrics | None = None,
    message: str = "ok",
) -> FeedSnapshot:
    """Build a consistent health snapshot for external feed services."""
    effective_quality = quality or FeedQualityMetrics()
    effective_latency = latency or FeedLatencyMetrics()
    effective_status = status
    if status == FeedStatus.RUNNING and (
        effective_quality.quality_score < 70 or effective_latency.threshold_breached
    ):
        effective_status = FeedStatus.DEGRADED
    return FeedSnapshot(
        source=source,
        status=effective_status,
        running=effective_status in {FeedStatus.RUNNING, FeedStatus.DEGRADED},
        symbols=symbols,
        timeframes=timeframes,
        uptime_seconds=uptime_seconds,
        reconnect_attempts=reconnect_attempts,
        latency=effective_latency,
        quality=effective_quality,
        message=message,
    )
