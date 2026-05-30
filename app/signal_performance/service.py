"""Signal performance validation orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.signal_intelligence.service import SignalIntelligenceService
from app.signal_performance.analytics import SignalPerformanceAnalytics
from app.signal_performance.confidence_validation import ConfidenceValidationEngine
from app.signal_performance.models import PaperTradeResult, SignalOutcome, TrackedSignal
from app.signal_performance.paper_trading import PaperTradingEngine
from app.signal_performance.reports import SignalPerformanceReportWriter
from app.signal_performance.storage import SignalPerformanceStorage
from app.signal_performance.tracker import SignalTracker


@dataclass(frozen=True)
class SignalPerformanceRunResult:
    """Result of one signal performance validation run."""

    tracked_signals: list[TrackedSignal]
    paper_results: list[PaperTradeResult]
    outcomes: list[SignalOutcome]
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class SignalPerformanceService:
    """Evaluate signal intelligence quality over historical candles."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.tracker = SignalTracker()
        self.paper = PaperTradingEngine()
        self.confidence = ConfidenceValidationEngine()
        self.analytics = SignalPerformanceAnalytics()
        self.storage = SignalPerformanceStorage(
            self.project_root / "storage" / "signal_performance"
        )
        self.reports = SignalPerformanceReportWriter(
            self.project_root / "reports" / "signal_performance"
        )

    def run(self) -> SignalPerformanceRunResult:
        intelligence = SignalIntelligenceService(self.project_root).run()
        payloads = [signal.to_dict() for signal in intelligence.snapshot.signals]
        tracked = self.tracker.track(payloads)
        paper_results = self.paper.evaluate(tracked, intelligence.snapshot.candles)
        outcomes = [result.outcome for result in paper_results]
        confidence_report = self.confidence.validate(paper_results).to_dict()
        analytics = self.analytics.summarize(paper_results, confidence_report)
        storage_paths = self.storage.save(tracked, paper_results, outcomes, analytics)
        report_paths = self.reports.export(analytics)
        return SignalPerformanceRunResult(
            tracked_signals=tracked,
            paper_results=paper_results,
            outcomes=outcomes,
            analytics=analytics,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )
