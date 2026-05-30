"""Multi-timeframe confirmation orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.multi_timeframe.analytics import MultiTimeframeAnalytics
from app.multi_timeframe.confirmation import MultiTimeframeConfirmationEngine
from app.multi_timeframe.models import ConfirmationResult
from app.multi_timeframe.reports import MultiTimeframeReportWriter
from app.multi_timeframe.storage import MultiTimeframeStorage
from app.opportunity_engine.service import OpportunityService


@dataclass(frozen=True)
class MultiTimeframeRunResult:
    """Result of one multi-timeframe confirmation cycle."""

    confirmations: list[ConfirmationResult]
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class MultiTimeframeService:
    """Confirm qualified opportunities across M1, M5, M15, and H1."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.engine = MultiTimeframeConfirmationEngine()
        self.analytics = MultiTimeframeAnalytics()
        self.storage = MultiTimeframeStorage(
            self.project_root / "storage" / "multi_timeframe"
        )
        self.reports = MultiTimeframeReportWriter(
            self.project_root / "reports" / "multi_timeframe"
        )

    def run(self) -> MultiTimeframeRunResult:
        opportunities = OpportunityService(self.project_root).run()
        rankings = [item.to_dict() for item in opportunities.rankings]
        confirmations = [self.engine.confirm(item) for item in rankings]
        analytics = self.analytics.summarize(confirmations)
        storage_paths = self.storage.save(confirmations, analytics)
        report_paths = self.reports.export(analytics)
        return MultiTimeframeRunResult(
            confirmations=confirmations,
            analytics=analytics,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )
