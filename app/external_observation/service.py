"""Passive external observation sandbox orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.external_observation.analytics import ExternalObservationAnalytics
from app.external_observation.diagnostics import ObservationDiagnosticsEngine
from app.external_observation.diagnostics import ObservationRecommendationEngine
from app.external_observation.isolation import IsolationEngine
from app.external_observation.models import ExternalObservationResult
from app.external_observation.monitoring import ObservationMonitoringEngine
from app.external_observation.reports import ExternalObservationReportWriter
from app.external_observation.sandbox import ExternalObservationSandbox
from app.external_observation.sandbox import ObservationHealthEngine
from app.external_observation.sources import ObservationSourceRegistry
from app.external_observation.storage import ExternalObservationStorage
from app.external_observation.validation import SourceValidationEngine


@dataclass(frozen=True)
class ExternalObservationRunResult:
    """Result of one passive external observation sandbox run."""

    result: ExternalObservationResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ExternalObservationService:
    """Evaluate the passive external observation sandbox."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.sources = ObservationSourceRegistry(self.project_root)
        self.validation = SourceValidationEngine()
        self.isolation = IsolationEngine()
        self.monitoring = ObservationMonitoringEngine()
        self.health = ObservationHealthEngine()
        self.sandbox = ExternalObservationSandbox()
        self.diagnostics = ObservationDiagnosticsEngine()
        self.recommendations = ObservationRecommendationEngine()
        self.analytics = ExternalObservationAnalytics()
        self.storage = ExternalObservationStorage(
            self.project_root / "storage" / "external_observation"
        )
        self.reports = ExternalObservationReportWriter(
            self.project_root / "reports" / "external_observation"
        )

    def run(self) -> ExternalObservationRunResult:
        sources = self.sources.discover()
        validation = self.validation.validate(sources)
        isolation = self.isolation.evaluate()
        monitoring = self.monitoring.monitor(sources, validation.score)
        health = self.health.evaluate(validation, monitoring, isolation, sources)
        sandbox = self.sandbox.score(validation, monitoring, isolation, health)
        diagnostics = self.diagnostics.evaluate(
            sources,
            validation,
            monitoring,
            isolation,
            health,
        )
        recommendations = self.recommendations.generate(diagnostics)
        result = ExternalObservationResult(
            timestamp=datetime.utcnow(),
            sources=sources,
            validation=validation,
            isolation=isolation,
            monitoring=monitoring,
            health=health,
            sandbox=sandbox,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata={
                "research_only": True,
                "observation_only": True,
                "not_execution": True,
                "not_order_placement": True,
                "not_account_login": True,
                "not_broker_authentication": True,
                "not_browser_automation": True,
                "not_broker_control": True,
            },
        )
        analytics = self.analytics.summarize(result)
        storage_paths = self.storage.save(result, analytics)
        report_paths = self.reports.export(analytics)
        return ExternalObservationRunResult(result, analytics, storage_paths, report_paths)
