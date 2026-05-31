"""Manual snapshot import workflow orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.snapshot_import.analytics import SnapshotImportAnalytics
from app.snapshot_import.diagnostics import SnapshotDiagnosticsEngine
from app.snapshot_import.diagnostics import SnapshotRecommendationEngine
from app.snapshot_import.importer import SnapshotImporter
from app.snapshot_import.models import SnapshotImportResult
from app.snapshot_import.parser import SnapshotParserEngine
from app.snapshot_import.processor import SnapshotProcessingEngine
from app.snapshot_import.processor import SnapshotQualityEngine
from app.snapshot_import.reports import SnapshotImportReportWriter
from app.snapshot_import.storage import SnapshotImportStorage
from app.snapshot_import.validator import SnapshotValidationEngine
from app.snapshot_import.workflow import SnapshotImportWorkflow
from app.snapshot_import.workflow import SnapshotSafetyEngine


@dataclass(frozen=True)
class SnapshotImportRunResult:
    """Result of one manual snapshot import workflow run."""

    result: SnapshotImportResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class SnapshotImportService:
    """Evaluate manually uploaded snapshot artifacts."""

    def __init__(
        self,
        project_root: Path | str = ".",
        max_size_bytes: int = 2_000_000,
    ) -> None:
        self.project_root = Path(project_root)
        self.max_size_bytes = max_size_bytes
        self.importer = SnapshotImporter(
            self.project_root,
            max_size_bytes=max_size_bytes,
        )
        self.validator = SnapshotValidationEngine(max_size_bytes=max_size_bytes)
        self.parser = SnapshotParserEngine()
        self.processor = SnapshotProcessingEngine()
        self.quality = SnapshotQualityEngine()
        self.safety = SnapshotSafetyEngine()
        self.workflow = SnapshotImportWorkflow()
        self.diagnostics = SnapshotDiagnosticsEngine()
        self.recommendations = SnapshotRecommendationEngine()
        self.analytics = SnapshotImportAnalytics()
        self.storage = SnapshotImportStorage(
            self.project_root / "storage" / "snapshot_import"
        )
        self.reports = SnapshotImportReportWriter(
            self.project_root / "reports" / "snapshot_import"
        )

    def run(self) -> SnapshotImportRunResult:
        imports = self.importer.register_uploads()
        validation = self.validator.validate(imports)
        parse = self.parser.parse(imports)
        processing = self.processor.process(imports, parse, validation)
        quality = self.quality.evaluate(imports, validation, processing)
        safety = self.safety.evaluate()
        workflow = self.workflow.score(validation, processing, quality, safety)
        diagnostics = self.diagnostics.evaluate(imports, validation, quality, safety)
        recommendations = self.recommendations.generate(diagnostics)
        result = SnapshotImportResult(
            timestamp=datetime.utcnow(),
            imports=imports,
            validation=validation,
            parse=parse,
            processing=processing,
            quality=quality,
            safety=safety,
            workflow=workflow,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata={
                "manual_only": True,
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
                "max_size_bytes": self.max_size_bytes,
            },
        )
        analytics = self.analytics.summarize(result)
        storage_paths = self.storage.save(result, analytics)
        report_paths = self.reports.export(analytics)
        return SnapshotImportRunResult(result, analytics, storage_paths, report_paths)
