"""Trade lifecycle research simulation orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.confluence.service import ConfluenceService
from app.trade_lifecycle.analytics import TradeLifecycleAnalytics
from app.trade_lifecycle.lifecycle import TradeLifecycleEngine
from app.trade_lifecycle.models import TradeLifecycleRecord
from app.trade_lifecycle.reports import TradeLifecycleReportWriter
from app.trade_lifecycle.storage import TradeLifecycleStorage


@dataclass(frozen=True)
class TradeLifecycleRunResult:
    """Result of one lifecycle simulation run."""

    records: list[TradeLifecycleRecord]
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class TradeLifecycleService:
    """Simulate and analyze research opportunity lifecycle records."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.engine = TradeLifecycleEngine()
        self.analytics = TradeLifecycleAnalytics()
        self.storage = TradeLifecycleStorage(
            self.project_root / "storage" / "trade_lifecycle"
        )
        self.reports = TradeLifecycleReportWriter(
            self.project_root / "reports" / "trade_lifecycle"
        )

    def run(self) -> TradeLifecycleRunResult:
        confluence = ConfluenceService(self.project_root).run()
        decisions = [item.to_dict() for item in confluence.decisions]
        records = [
            self.engine.simulate(decision, index)
            for index, decision in enumerate(decisions)
        ]
        analytics = self.analytics.summarize(records)
        storage_paths = self.storage.save(records, analytics)
        report_paths = self.reports.export(analytics)
        return TradeLifecycleRunResult(
            records=records,
            analytics=analytics,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )
