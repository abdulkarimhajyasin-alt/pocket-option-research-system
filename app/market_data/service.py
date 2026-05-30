"""Service layer for provider-based market data research integration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.market_data.analytics import MarketAnalytics
from app.market_data.models import MarketSnapshot
from app.market_data.providers import BaseMarketDataProvider, StaticResearchProvider
from app.market_data.reports import MarketDataReportWriter
from app.market_data.storage import MarketDataStorage


@dataclass(frozen=True)
class MarketDataRunResult:
    """Result of one market-data integration cycle."""

    snapshot: MarketSnapshot
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


class MarketDataService:
    """Collect, validate, analyze, store, and report market data."""

    def __init__(
        self,
        project_root: Path | str = ".",
        provider: BaseMarketDataProvider | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.provider = provider or StaticResearchProvider()
        self.analytics = MarketAnalytics()
        self.storage = MarketDataStorage(self.project_root / "storage" / "market_data")
        self.reports = MarketDataReportWriter(
            self.project_root / "reports" / "market_data"
        )

    def collect(self) -> MarketSnapshot:
        """Collect one provider snapshot."""
        snapshot = self.provider.snapshot()
        self.validate(snapshot)
        return self.normalize(snapshot)

    def validate(self, snapshot: MarketSnapshot) -> None:
        """Validate provider snapshot and research-only metadata."""
        if snapshot.metadata.get("research_only") is not True:
            raise ValueError("Market data integration must remain research-only")
        if snapshot.metadata.get("no_execution") is not True:
            raise ValueError("Market data integration must not provide execution")
        if not snapshot.assets:
            raise ValueError("Market data snapshot requires assets")
        if not snapshot.sessions:
            raise ValueError("Market data snapshot requires sessions")
        if not snapshot.statuses:
            raise ValueError("Market data snapshot requires market status")

    def normalize(self, snapshot: MarketSnapshot) -> MarketSnapshot:
        """Normalize deterministic ordering without changing provider contract."""
        return MarketSnapshot(
            timestamp=snapshot.timestamp,
            provider=snapshot.provider,
            asset=snapshot.asset,
            timeframe=snapshot.timeframe,
            metadata={**snapshot.metadata, "normalized": True},
            provider_info=snapshot.provider_info,
            assets=tuple(sorted(snapshot.assets, key=lambda item: item.asset)),
            candles=tuple(
                sorted(snapshot.candles, key=lambda item: (item.asset, item.timestamp))
            ),
            sessions=tuple(sorted(snapshot.sessions, key=lambda item: item.name)),
            statuses=tuple(sorted(snapshot.statuses, key=lambda item: item.asset)),
            latencies=tuple(sorted(snapshot.latencies, key=lambda item: item.asset)),
            health=snapshot.health,
        )

    def run(self) -> MarketDataRunResult:
        """Run a complete market-data integration cycle."""
        snapshot = self.collect()
        analytics = self.analytics.summarize(snapshot)
        storage_paths = self.storage.save(snapshot, analytics)
        report_paths = self.reports.export(analytics)
        return MarketDataRunResult(
            snapshot=snapshot,
            analytics=analytics,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )
