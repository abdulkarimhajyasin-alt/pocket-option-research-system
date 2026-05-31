"""Passive broker observation readiness orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.broker_readiness.analytics import BrokerReadinessAnalytics
from app.broker_readiness.capabilities import CapabilityAssessmentEngine
from app.broker_readiness.diagnostics import BrokerReadinessDiagnostics
from app.broker_readiness.diagnostics import BrokerReadinessRecommendationEngine
from app.broker_readiness.models import BrokerReadinessResult
from app.broker_readiness.observation import ObservationCapabilityBuilder
from app.broker_readiness.readiness import BrokerObservationReadinessEngine
from app.broker_readiness.reports import BrokerReadinessReportWriter
from app.broker_readiness.restrictions import SafetyRestrictionEngine
from app.broker_readiness.storage import BrokerReadinessStorage
from app.broker_readiness.validation import ObservationValidationEngine


@dataclass(frozen=True)
class BrokerReadinessRunResult:
    """Result of one passive broker readiness run."""

    result: BrokerReadinessResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class BrokerReadinessService:
    """Evaluate passive broker observation readiness."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.observation = ObservationCapabilityBuilder(self.project_root)
        self.capabilities = CapabilityAssessmentEngine()
        self.restrictions = SafetyRestrictionEngine()
        self.validation = ObservationValidationEngine()
        self.readiness = BrokerObservationReadinessEngine()
        self.diagnostics = BrokerReadinessDiagnostics()
        self.recommendations = BrokerReadinessRecommendationEngine()
        self.analytics = BrokerReadinessAnalytics()
        self.storage = BrokerReadinessStorage(
            self.project_root / "storage" / "broker_readiness"
        )
        self.reports = BrokerReadinessReportWriter(
            self.project_root / "reports" / "broker_readiness"
        )

    def run(self) -> BrokerReadinessRunResult:
        capability = self.observation.build()
        assessment = self.capabilities.assess(capability)
        restrictions = self.restrictions.evaluate()
        validation = self.validation.validate(assessment, restrictions)
        readiness = self.readiness.evaluate(assessment, validation, restrictions)
        diagnostics = self.diagnostics.evaluate(readiness, validation, restrictions)
        recommendations = self.recommendations.generate(diagnostics)
        result = BrokerReadinessResult(
            timestamp=datetime.utcnow(),
            capability=capability,
            assessment=assessment,
            validation=validation,
            restrictions=restrictions,
            readiness=readiness,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata={
                "research_only": True,
                "observation_only": True,
                "not_execution": True,
                "not_order_placement": True,
                "not_account_action": True,
                "not_automation": True,
                "not_broker_control": True,
            },
        )
        analytics = self.analytics.summarize(result)
        storage_paths = self.storage.save(result, analytics)
        report_paths = self.reports.export(analytics)
        return BrokerReadinessRunResult(result, analytics, storage_paths, report_paths)
