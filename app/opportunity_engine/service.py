"""Opportunity qualification orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.opportunity_engine.analytics import OpportunityAnalytics
from app.opportunity_engine.models import OpportunityRanking, QualifiedOpportunity
from app.opportunity_engine.qualification import OpportunityQualificationEngine
from app.opportunity_engine.ranking import OpportunityRankingEngine
from app.opportunity_engine.reports import OpportunityReportWriter
from app.opportunity_engine.storage import OpportunityStorage
from app.signal_intelligence.service import SignalIntelligenceService


@dataclass(frozen=True)
class OpportunityRunResult:
    """Result of one opportunity qualification run."""

    opportunities: list[QualifiedOpportunity]
    rankings: list[OpportunityRanking]
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class OpportunityService:
    """Generate, qualify, rank, store, and report research opportunities."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.qualifier = OpportunityQualificationEngine()
        self.ranker = OpportunityRankingEngine()
        self.analytics = OpportunityAnalytics()
        self.storage = OpportunityStorage(self.project_root / "storage" / "opportunities")
        self.reports = OpportunityReportWriter(
            self.project_root / "reports" / "opportunities"
        )

    def run(self) -> OpportunityRunResult:
        intelligence = SignalIntelligenceService(self.project_root).run()
        signals = [signal.to_dict() for signal in intelligence.snapshot.signals]
        opportunities = [self.qualifier.qualify(signal) for signal in signals]
        rankings = self.ranker.rank(opportunities)
        analytics = self.analytics.summarize(opportunities, rankings)
        storage_paths = self.storage.save(opportunities, rankings, analytics)
        report_paths = self.reports.export(analytics)
        return OpportunityRunResult(
            opportunities=opportunities,
            rankings=rankings,
            analytics=analytics,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )
