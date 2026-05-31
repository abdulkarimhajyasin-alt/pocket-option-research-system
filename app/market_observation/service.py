"""Canonical market observation service orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.market_observation.aggregator import MarketObservationAggregator
from app.market_observation.analytics import MarketObservationAnalytics
from app.market_observation.diagnostics import MarketObservationDiagnosticsEngine
from app.market_observation.models import MarketObservationResult
from app.market_observation.normalizer import MarketObservationNormalizer
from app.market_observation.reports import MarketObservationReportWriter
from app.market_observation.storage import MarketObservationStorage
from app.market_observation.validation import MarketObservationValidationEngine


@dataclass(frozen=True)
class MarketObservationRunResult:
    """Result of one canonical market observation run."""

    result: MarketObservationResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class MarketObservationService:
    """Build the canonical research-only market observation source."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.normalizer = MarketObservationNormalizer(self.project_root)
        self.validation = MarketObservationValidationEngine()
        self.aggregator = MarketObservationAggregator()
        self.diagnostics = MarketObservationDiagnosticsEngine()
        self.analytics = MarketObservationAnalytics()
        self.storage = MarketObservationStorage(
            self.project_root / "storage" / "market_observation"
        )
        self.reports = MarketObservationReportWriter(
            self.project_root / "reports" / "market_observation"
        )

    def run(self) -> MarketObservationRunResult:
        observations = self.normalizer.normalize()
        validation = self.validation.validate(observations)
        aggregate = self.aggregator.aggregate(observations, validation)
        diagnostics = self.diagnostics.evaluate(validation, aggregate)
        result = MarketObservationResult(
            timestamp=datetime.now(UTC),
            observations=observations,
            validation=validation,
            aggregate=aggregate,
            diagnostics=diagnostics,
            metadata={
                "research_only": True,
                "observation_only": True,
                "canonical_market_observation": True,
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
        return MarketObservationRunResult(result, analytics, storage_paths, report_paths)
