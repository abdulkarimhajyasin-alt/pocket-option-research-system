"""Dataset comparison engine."""

from __future__ import annotations

from uuid import uuid4

from app.datasets.models import DatasetComparisonReport, DatasetStatistics


class DatasetComparisonEngine:
    """Compare research datasets by quality, coverage, and stability indicators."""

    def compare(self, statistics: list[DatasetStatistics]) -> DatasetComparisonReport:
        """Return ranked dataset comparison report."""
        rankings = sorted(
            (self._rank_payload(item) for item in statistics),
            key=lambda item: (
                -float(item["quality_score"]),
                int(item["gap_count"]),
                int(item["duplicate_count"]),
                -int(item["row_count"]),
            ),
        )
        comparisons = []
        for left, right in zip(statistics, statistics[1:]):
            comparisons.append(
                {
                    "left": left.dataset_name,
                    "right": right.dataset_name,
                    "row_count_delta": right.row_count - left.row_count,
                    "quality_delta": round(right.quality_score - left.quality_score, 4),
                    "volatility_delta": round(
                        right.volatility_estimate - left.volatility_estimate,
                        8,
                    ),
                    "gap_delta": right.gap_count - left.gap_count,
                    "duplicate_delta": right.duplicate_count - left.duplicate_count,
                }
            )
        return DatasetComparisonReport(
            report_id=str(uuid4()),
            datasets=[item.dataset_name for item in statistics],
            rankings=rankings,
            comparisons=comparisons,
        )

    def _rank_payload(self, item: DatasetStatistics) -> dict[str, object]:
        return {
            "dataset_id": item.dataset_id,
            "dataset_name": item.dataset_name,
            "row_count": item.row_count,
            "quality_score": item.quality_score,
            "volatility": item.volatility_estimate,
            "gap_count": item.gap_count,
            "duplicate_count": item.duplicate_count,
        }
