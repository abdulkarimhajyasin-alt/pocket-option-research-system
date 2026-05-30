"""Service layer for collecting and publishing market observations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.observation.analytics import ObservationAnalytics
from app.observation.models import BrokerSnapshot
from app.observation.provider import MockObservationProvider, ObservationProvider
from app.observation.storage import ObservationReportWriter, ObservationStorage


@dataclass(frozen=True)
class ObservationRunResult:
    """Result of one observation collection run."""

    snapshot: BrokerSnapshot
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


class ObservationService:
    """Collect, validate, normalize, publish, and store observations."""

    def __init__(
        self,
        project_root: Path | str = ".",
        provider: ObservationProvider | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.provider = provider or MockObservationProvider()
        self.analytics = ObservationAnalytics()
        self.storage = ObservationStorage(self.project_root / "storage" / "observations")
        self.reports = ObservationReportWriter(
            self.project_root / "reports" / "observation"
        )

    def collect(self) -> BrokerSnapshot:
        """Collect and normalize one observation snapshot."""
        snapshot = self.provider.get_market_snapshot()
        self.validate(snapshot)
        return self.normalize(snapshot)

    def validate(self, snapshot: BrokerSnapshot) -> None:
        """Validate minimum snapshot completeness."""
        if not snapshot.assets:
            raise ValueError("Observation snapshot requires asset observations")
        if not snapshot.payouts:
            raise ValueError("Observation snapshot requires payout observations")
        if not snapshot.sessions:
            raise ValueError("Observation snapshot requires session observations")

    def normalize(self, snapshot: BrokerSnapshot) -> BrokerSnapshot:
        """Return a deterministic ordering for downstream analytics."""
        return BrokerSnapshot(
            timestamp=snapshot.timestamp,
            asset=snapshot.asset,
            timeframe=snapshot.timeframe,
            source=snapshot.source,
            metadata={**snapshot.metadata, "normalized": True},
            assets=tuple(sorted(snapshot.assets, key=lambda item: item.asset)),
            markets=tuple(sorted(snapshot.markets, key=lambda item: item.asset)),
            payouts=tuple(sorted(snapshot.payouts, key=lambda item: item.asset)),
            sessions=tuple(sorted(snapshot.sessions, key=lambda item: item.session_name)),
            candles=tuple(
                sorted(snapshot.candles, key=lambda item: (item.asset, item.timestamp))
            ),
        )

    def publish(self, snapshot: BrokerSnapshot) -> dict[str, Any]:
        """Publish observation summary as local in-process data."""
        return self.analytics.summarize(snapshot)

    def store(
        self,
        snapshot: BrokerSnapshot,
        analytics: dict[str, Any],
    ) -> dict[str, dict[str, str]]:
        """Persist storage and report artifacts."""
        return {
            "storage": self.storage.save_snapshot(snapshot),
            "reports": self.reports.export(analytics),
        }

    def run(self) -> ObservationRunResult:
        """Run the full observation collection workflow."""
        snapshot = self.collect()
        analytics = self.publish(snapshot)
        paths = self.store(snapshot, analytics)
        return ObservationRunResult(
            snapshot=snapshot,
            analytics=analytics,
            storage_paths=paths["storage"],
            report_paths=paths["reports"],
        )
