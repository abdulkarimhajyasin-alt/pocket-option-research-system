"""Confluence research orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.confluence.analytics import ConfluenceAnalytics
from app.confluence.confluence import ConfluenceEngine, ResearchDecisionEngine
from app.confluence.models import ResearchDecision
from app.confluence.reports import ConfluenceReportWriter
from app.confluence.storage import ConfluenceStorage
from app.multi_timeframe.service import MultiTimeframeService
from app.opportunity_engine.service import OpportunityService
from app.signal_intelligence.service import SignalIntelligenceService
from app.signal_performance.service import SignalPerformanceService


@dataclass(frozen=True)
class ConfluenceRunResult:
    """Result of one confluence research cycle."""

    decisions: list[ResearchDecision]
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ConfluenceService:
    """Run all research engines and create unified confluence decisions."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.engine = ConfluenceEngine()
        self.decision_engine = ResearchDecisionEngine()
        self.analytics = ConfluenceAnalytics()
        self.storage = ConfluenceStorage(self.project_root / "storage" / "confluence")
        self.reports = ConfluenceReportWriter(
            self.project_root / "reports" / "confluence"
        )

    def run(self) -> ConfluenceRunResult:
        signal_run = SignalIntelligenceService(self.project_root).run()
        performance_run = SignalPerformanceService(self.project_root).run()
        opportunity_run = OpportunityService(self.project_root).run()
        timeframe_run = MultiTimeframeService(self.project_root).run()

        opportunities = {
            item.opportunity.opportunity_id: item.opportunity.to_dict()
            for item in opportunity_run.rankings
        }
        signal_summary = signal_run.analytics.get("summary", signal_run.analytics)
        performance_summary = performance_run.analytics.get("summary", {})
        session_performance = performance_run.analytics.get("session_performance", {})

        decisions = []
        for confirmation in timeframe_run.confirmations:
            confirmation_payload = confirmation.to_dict()
            opportunity = opportunities.get(confirmation.opportunity_id)
            if opportunity is None:
                continue
            confluence = self.engine.evaluate(
                opportunity=opportunity,
                confirmation=confirmation_payload,
                signal_summary=signal_summary,
                performance_summary=performance_summary,
                session_performance=session_performance,
            )
            decisions.append(self.decision_engine.decide(confluence))

        decisions.sort(key=lambda item: item.confluence_score, reverse=True)
        analytics = self.analytics.summarize(decisions)
        storage_paths = self.storage.save(decisions, analytics)
        report_paths = self.reports.export(analytics)
        return ConfluenceRunResult(
            decisions=decisions,
            analytics=analytics,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )
