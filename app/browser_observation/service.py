"""Read-only browser observation orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.browser_observation.adapter import ReadOnlyObservationAdapter
from app.browser_observation.analytics import BrowserObservationAnalytics
from app.browser_observation.diagnostics import BrowserObservationDiagnostics
from app.browser_observation.diagnostics import BrowserObservationRecommendationEngine
from app.browser_observation.models import BrowserObservationResult
from app.browser_observation.monitoring import ArtifactMonitoringEngine
from app.browser_observation.parser import ArtifactParserEngine
from app.browser_observation.reports import BrowserObservationReportWriter
from app.browser_observation.safety import ReadOnlySafetyEngine
from app.browser_observation.storage import BrowserObservationStorage
from app.browser_observation.validator import ArtifactValidationEngine
from app.browser_observation.visibility import VisibilityAssessmentEngine


@dataclass(frozen=True)
class BrowserObservationRunResult:
    """Result of one read-only browser observation run."""

    result: BrowserObservationResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class BrowserObservationService:
    """Evaluate externally supplied read-only browser observation artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.adapter = ReadOnlyObservationAdapter(self.project_root)
        self.parser = ArtifactParserEngine()
        self.validator = ArtifactValidationEngine()
        self.visibility = VisibilityAssessmentEngine()
        self.monitoring = ArtifactMonitoringEngine()
        self.safety = ReadOnlySafetyEngine()
        self.diagnostics = BrowserObservationDiagnostics()
        self.recommendations = BrowserObservationRecommendationEngine()
        self.analytics = BrowserObservationAnalytics()
        self.storage = BrowserObservationStorage(
            self.project_root / "storage" / "browser_observation"
        )
        self.reports = BrowserObservationReportWriter(
            self.project_root / "reports" / "browser_observation"
        )

    def run(self) -> BrowserObservationRunResult:
        artifacts = self.adapter.load_artifacts()
        parse = self.parser.parse(artifacts)
        validation = self.validator.validate(artifacts)
        visibility = self.visibility.assess(artifacts, parse)
        monitoring = self.monitoring.monitor(artifacts, validation, visibility)
        safety = self.safety.evaluate()
        adapter = self.adapter.score(
            parse.score,
            validation.score,
            visibility.score,
            monitoring.score,
            safety.score,
        )
        diagnostics = self.diagnostics.evaluate(
            artifacts,
            validation,
            visibility,
            monitoring,
            safety,
        )
        recommendations = self.recommendations.generate(diagnostics)
        result = BrowserObservationResult(
            timestamp=datetime.utcnow(),
            artifacts=artifacts,
            parse=parse,
            validation=validation,
            visibility=visibility,
            monitoring=monitoring,
            safety=safety,
            adapter=adapter,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata={
                "research_only": True,
                "observation_only": True,
                "read_only": True,
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
        return BrowserObservationRunResult(result, analytics, storage_paths, report_paths)
