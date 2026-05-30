"""Service layer for live market feed observation pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.live_feed.analytics import LiveFeedAnalytics
from app.live_feed.buffer import FeedBuffer
from app.live_feed.models import FeedSnapshot
from app.live_feed.provider import MarketFeedProvider, MockLiveFeedProvider
from app.live_feed.storage import LiveFeedReportWriter, LiveFeedStorage


@dataclass(frozen=True)
class LiveFeedRunResult:
    """Result of one live feed research pipeline run."""

    snapshot: FeedSnapshot
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot": self.snapshot.to_dict(),
            "analytics": self.analytics,
            "storage_paths": self.storage_paths,
            "report_paths": self.report_paths,
        }


class LiveFeedService:
    """Consume, validate, normalize, publish, and store feed observations."""

    def __init__(
        self,
        project_root: Path | str = ".",
        provider: MarketFeedProvider | None = None,
        buffer: FeedBuffer | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.provider = provider or MockLiveFeedProvider()
        self.buffer = buffer or FeedBuffer()
        self.analytics = LiveFeedAnalytics()
        self.storage = LiveFeedStorage(self.project_root / "storage" / "live_feed")
        self.reports = LiveFeedReportWriter(self.project_root / "reports" / "live_feed")

    def consume(self) -> FeedSnapshot:
        """Consume one latest snapshot from the configured provider."""
        self.provider.connect()
        self.provider.subscribe(["EURUSD", "GBPUSD", "USDJPY"], ["1m", "5m", "15m"])
        snapshot = self.provider.get_latest()
        self.validate(snapshot)
        normalized = self.normalize(snapshot)
        self.buffer.update_snapshot(normalized)
        return normalized

    def validate(self, snapshot: FeedSnapshot) -> None:
        """Validate minimum live-feed completeness."""
        if not snapshot.ticks:
            raise ValueError("Live feed snapshot requires tick updates")
        if not snapshot.candles:
            raise ValueError("Live feed snapshot requires candle updates")
        if snapshot.metadata.get("no_broker_connection") is not True:
            raise ValueError("Live feed provider must remain mock/no-broker in this phase")

    def normalize(self, snapshot: FeedSnapshot) -> FeedSnapshot:
        """Return a deterministic ordering for downstream analytics."""
        return FeedSnapshot(
            timestamp=snapshot.timestamp,
            source=snapshot.source,
            asset=snapshot.asset,
            timeframe=snapshot.timeframe,
            metadata={**snapshot.metadata, "normalized": True},
            ticks=tuple(sorted(snapshot.ticks, key=lambda item: (item.asset, item.timestamp))),
            candles=tuple(
                sorted(
                    snapshot.candles,
                    key=lambda item: (item.asset, item.timeframe, item.timestamp),
                )
            ),
            latencies=snapshot.latencies,
            statistics=snapshot.statistics,
            health=snapshot.health,
        )

    def publish(self, snapshot: FeedSnapshot) -> dict[str, Any]:
        """Publish analytics as local in-process data."""
        return self.analytics.summarize(snapshot)

    def run(self) -> LiveFeedRunResult:
        """Run one observation-only live-feed pipeline cycle."""
        snapshot = self.consume()
        analytics = self.publish(snapshot)
        storage_paths = self.storage.save(snapshot, analytics)
        report_paths = self.reports.export(analytics)
        return LiveFeedRunResult(
            snapshot=snapshot,
            analytics=analytics,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )
