"""Processing and quality engines for manual snapshot imports."""

from __future__ import annotations

from app.snapshot_import.models import ParseResult
from app.snapshot_import.models import ProcessingResult
from app.snapshot_import.models import QualityResult
from app.snapshot_import.models import SnapshotImport
from app.snapshot_import.models import ValidationResult
from app.snapshot_import.validator import average
from app.snapshot_import.validator import clamp


class SnapshotProcessingEngine:
    """Process parsed data, visibility, completeness, and quality metrics."""

    def process(
        self,
        imports: tuple[SnapshotImport, ...],
        parse: ParseResult,
        validation: ValidationResult,
    ) -> ProcessingResult:
        count = len(imports)
        ready = sum(1 for item in imports if item.processing_status == "جاهز")
        parsed_data = parse.score
        visibility_metrics = min(100.0, parse.market_information * 20.0)
        completeness_metrics = validation.file_completeness
        quality_metrics = (ready / count * 100.0) if count else 0.0
        return ProcessingResult(
            score=average(
                [
                    parsed_data,
                    visibility_metrics,
                    completeness_metrics,
                    quality_metrics,
                ]
            ),
            parsed_data=clamp(parsed_data),
            visibility_metrics=clamp(visibility_metrics),
            completeness_metrics=clamp(completeness_metrics),
            quality_metrics=clamp(quality_metrics),
        )


class SnapshotQualityEngine:
    """Evaluate quality, visibility, completeness, consistency, and freshness."""

    def evaluate(
        self,
        imports: tuple[SnapshotImport, ...],
        validation: ValidationResult,
        processing: ProcessingResult,
    ) -> QualityResult:
        count = len(imports)
        readable = sum(1 for item in imports if item.metadata.get("readable"))
        fresh = sum(1 for item in imports if item.imported_at != "0")
        quality = average([validation.score, processing.quality_metrics])
        visibility = processing.visibility_metrics
        completeness = validation.file_completeness
        consistency = (readable / count * 100.0) if count else 0.0
        freshness = (fresh / count * 100.0) if count else 0.0
        return QualityResult(
            score=average([quality, visibility, completeness, consistency, freshness]),
            quality=clamp(quality),
            visibility=clamp(visibility),
            completeness=clamp(completeness),
            consistency=clamp(consistency),
            freshness=clamp(freshness),
        )
