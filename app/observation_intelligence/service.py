"""Unified observation intelligence orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.observation_intelligence.aggregator import ObservationAggregator
from app.observation_intelligence.analytics import ObservationIntelligenceAnalytics
from app.observation_intelligence.diagnostics import ObservationDiagnosticsEngine
from app.observation_intelligence.diagnostics import ObservationRecommendationEngine
from app.observation_intelligence.intelligence import ObservationIntelligenceEngine
from app.observation_intelligence.models import ObservationIntelligenceResult
from app.observation_intelligence.normalizer import ObservationNormalizer
from app.observation_intelligence.reports import ObservationIntelligenceReportWriter
from app.observation_intelligence.storage import ObservationIntelligenceStorage
from app.observation_intelligence.validation import ObservationConfidenceEngine
from app.observation_intelligence.validation import ObservationQualityEngine
from app.observation_intelligence.validation import ObservationValidationEngine


@dataclass(frozen=True)
class ObservationIntelligenceRunResult:
    result: ObservationIntelligenceResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ObservationIntelligenceService:
    """Evaluate unified observation intelligence from local passive artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.normalizer = ObservationNormalizer(self.project_root)
        self.aggregator = ObservationAggregator()
        self.validation = ObservationValidationEngine()
        self.confidence = ObservationConfidenceEngine()
        self.quality = ObservationQualityEngine()
        self.intelligence = ObservationIntelligenceEngine()
        self.diagnostics = ObservationDiagnosticsEngine()
        self.recommendations = ObservationRecommendationEngine()
        self.analytics = ObservationIntelligenceAnalytics()
        self.storage = ObservationIntelligenceStorage(
            self.project_root / "storage" / "observation_intelligence"
        )
        self.reports = ObservationIntelligenceReportWriter(
            self.project_root / "reports" / "observation_intelligence"
        )

    def run(self) -> ObservationIntelligenceRunResult:
        observations, normalization = self.normalizer.normalize()
        aggregation = self.aggregator.aggregate(observations)
        validation = self.validation.validate(observations, aggregation)
        confidence = self.confidence.evaluate(observations, aggregation)
        quality = self.quality.evaluate(observations, aggregation, validation)
        intelligence = self.intelligence.evaluate(
            aggregation,
            validation,
            confidence,
            quality,
        )
        diagnostics = self.diagnostics.evaluate(
            observations,
            aggregation,
            confidence,
            quality,
        )
        recommendations = self.recommendations.generate(diagnostics)
        result = ObservationIntelligenceResult(
            timestamp=datetime.utcnow(),
            observations=observations,
            normalization=normalization,
            aggregation=aggregation,
            validation=validation,
            confidence=confidence,
            quality=quality,
            intelligence=intelligence,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata={
                "research_only": True,
                "observation_only": True,
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
        return ObservationIntelligenceRunResult(
            result,
            analytics,
            storage_paths,
            report_paths,
        )
