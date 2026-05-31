"""Signal stream service orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.signal_stream.analytics import SignalStreamAnalytics
from app.signal_stream.diagnostics import SignalStreamDiagnostics
from app.signal_stream.diagnostics import SignalStreamRecommendationEngine
from app.signal_stream.models import SignalStreamRun
from app.signal_stream.queue import SignalQueueEngine
from app.signal_stream.reports import SignalStreamReportWriter
from app.signal_stream.scoring import SignalStreamScoringEngine
from app.signal_stream.storage import SignalStreamStorage
from app.signal_stream.stream import SignalStreamEngine
from app.signal_stream.timeline import SignalTimelineEngine
from app.signal_stream.validation import SignalStreamValidationEngine


@dataclass(frozen=True)
class SignalStreamRunResult:
    """Result of one signal stream cycle."""

    result: SignalStreamRun
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class SignalStreamService:
    """Generate research-only signal stream events from observation replay."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.stream = SignalStreamEngine(self.project_root)
        self.queue = SignalQueueEngine()
        self.timeline = SignalTimelineEngine()
        self.scoring = SignalStreamScoringEngine()
        self.validation = SignalStreamValidationEngine()
        self.diagnostics = SignalStreamDiagnostics()
        self.recommendations = SignalStreamRecommendationEngine()
        self.analytics = SignalStreamAnalytics()
        self.storage = SignalStreamStorage(self.project_root / "storage" / "signal_stream")
        self.reports = SignalStreamReportWriter(self.project_root / "reports" / "signal_stream")

    def run(self) -> SignalStreamRunResult:
        stream = self.stream.run()
        queue = self.queue.manage(stream.events)
        timeline = self.timeline.build(stream.events)
        scoring = self.scoring.evaluate(stream.events)
        validation = self.validation.validate(stream.events, timeline)
        diagnostics = self.diagnostics.evaluate(stream.events, scoring, validation)
        recommendations = self.recommendations.generate(diagnostics)
        result = SignalStreamRun(
            timestamp=datetime.now(UTC),
            stream=stream,
            queue=queue,
            timeline=timeline,
            scoring=scoring,
            validation=validation,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata={
                "research_only": True,
                "signal_generation_only": True,
                "not_execution": True,
                "not_order_placement": True,
                "not_account_login": True,
                "not_broker_authentication": True,
                "not_credential_handling": True,
                "not_browser_automation": True,
                "not_broker_control": True,
            },
        )
        analytics = self.analytics.summarize(result)
        storage_paths = self.storage.save(result, analytics)
        report_paths = self.reports.export(analytics)
        return SignalStreamRunResult(result, analytics, storage_paths, report_paths)
