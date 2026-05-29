"""Dataset quality analytics."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from app.datasets.models import DatasetComparisonReport, DatasetStatistics, QualityReport


@dataclass(frozen=True)
class DatasetQualitySnapshot:
    """Analytics snapshot for dataset research quality."""

    dataset_id: str
    dataset_name: str
    quality_score: float
    row_count: int
    gap_count: int
    duplicate_count: int
    volatility_estimate: float
    warning_count: int
    error_count: int

    def to_dict(self) -> dict[str, object]:
        """Return serializable analytics snapshot."""
        return asdict(self)


class DatasetQualityAnalyzer:
    """Build analytics payloads for dataset quality reports."""

    def analyze(
        self,
        statistics: DatasetStatistics,
        quality: QualityReport,
    ) -> DatasetQualitySnapshot:
        """Return compact dataset quality analytics."""
        return DatasetQualitySnapshot(
            dataset_id=statistics.dataset_id,
            dataset_name=statistics.dataset_name,
            quality_score=statistics.quality_score,
            row_count=statistics.row_count,
            gap_count=statistics.gap_count,
            duplicate_count=statistics.duplicate_count,
            volatility_estimate=statistics.volatility_estimate,
            warning_count=len(quality.warnings),
            error_count=len(quality.errors),
        )

    def compare(self, report: DatasetComparisonReport) -> dict[str, object]:
        """Return comparison analytics summary."""
        best = report.rankings[0] if report.rankings else {}
        return {
            "report_id": report.report_id,
            "dataset_count": len(report.datasets),
            "best_dataset": best.get("dataset_name"),
            "best_quality_score": best.get("quality_score"),
            "comparisons": len(report.comparisons),
        }
