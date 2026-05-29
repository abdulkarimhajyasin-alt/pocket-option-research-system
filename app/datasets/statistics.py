"""Dataset statistics engine."""

from __future__ import annotations

from app.data.models import Candle
from app.datasets.models import DatasetMetadata, DatasetStatistics, QualityReport
from app.validation.statistics import population_stdev


class DatasetStatisticsEngine:
    """Generate compact research statistics for datasets."""

    def calculate(
        self,
        candles: list[Candle] | tuple[Candle, ...],
        metadata: DatasetMetadata,
        quality: QualityReport,
    ) -> DatasetStatistics:
        """Calculate deterministic dataset statistics."""
        if not candles:
            return DatasetStatistics(
                dataset_id=metadata.dataset_id,
                dataset_name=metadata.dataset_name,
                row_count=0,
                start_time=None,
                end_time=None,
                average_candle_size=0.0,
                volatility_estimate=0.0,
                gap_count=0,
                duplicate_count=0,
                quality_score=quality.quality_score,
            )
        ranges = [candle.high - candle.low for candle in candles]
        closes = [candle.close for candle in candles]
        returns = [
            (current - previous) / previous
            for previous, current in zip(closes, closes[1:])
            if previous
        ]
        duplicate_count = sum(
            issue.count for issue in quality.warnings if issue.code == "duplicate_candles"
        )
        return DatasetStatistics(
            dataset_id=metadata.dataset_id,
            dataset_name=metadata.dataset_name,
            row_count=len(candles),
            start_time=metadata.start_time,
            end_time=metadata.end_time,
            average_candle_size=round(sum(ranges) / len(ranges), 8),
            volatility_estimate=round(population_stdev(returns), 8) if returns else 0.0,
            gap_count=len(quality.gaps),
            duplicate_count=duplicate_count,
            quality_score=quality.quality_score,
        )
