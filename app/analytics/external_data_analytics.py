"""Analytics reporting for read-only external data feeds."""

from dataclasses import dataclass

from app.external_data.models import FeedSnapshot


@dataclass(frozen=True)
class ExternalDataAnalyticsSnapshot:
    """Compact feed quality, latency, reliability, and availability report."""

    source: str
    quality_score: float
    average_latency_ms: float
    reliability_score: float
    availability_score: float
    reconnect_attempts: int
    status: str

    def to_dict(self) -> dict[str, float | int | str]:
        """Return serializable analytics."""
        return self.__dict__.copy()


class ExternalDataAnalytics:
    """Build research analytics from external feed health snapshots."""

    def analyze(self, snapshot: FeedSnapshot) -> ExternalDataAnalyticsSnapshot:
        """Return compact external data analytics."""
        reconnect_penalty = min(40.0, snapshot.reconnect_attempts * 10.0)
        reliability = max(0.0, snapshot.quality.quality_score - reconnect_penalty)
        availability = 100.0 if snapshot.running else 0.0
        if snapshot.status.value == "degraded":
            availability = 75.0
        return ExternalDataAnalyticsSnapshot(
            source=snapshot.source,
            quality_score=round(snapshot.quality.quality_score, 4),
            average_latency_ms=round(snapshot.latency.average_ms, 4),
            reliability_score=round(reliability, 4),
            availability_score=availability,
            reconnect_attempts=snapshot.reconnect_attempts,
            status=snapshot.status.value,
        )
