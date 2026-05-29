"""Research dataset quality scoring."""

from __future__ import annotations

from collections import Counter

from app.data.models import Candle
from app.datasets.gaps import GapDetector
from app.datasets.models import GapSeverity, QualityIssue, QualityReport
from app.datasets.utils import parse_timeframe_seconds


class DataQualityEngine:
    """Validate and score normalized research datasets."""

    def __init__(self, gap_detector: GapDetector | None = None) -> None:
        self.gap_detector = gap_detector or GapDetector()

    def analyze(
        self,
        candles: list[Candle] | tuple[Candle, ...],
        dataset_id: str,
        dataset_name: str,
        symbol: str,
        timeframe: str,
    ) -> QualityReport:
        """Return explainable quality report."""
        warnings: list[QualityIssue] = []
        errors: list[QualityIssue] = []
        components = {
            "missing_data": 100.0,
            "duplicates": 100.0,
            "ordering": 100.0,
            "ohlc": 100.0,
            "volume": 100.0,
            "timeframe_consistency": 100.0,
        }
        if not candles:
            errors.append(QualityIssue("empty_dataset", "error", "Dataset contains no candles"))
            return QualityReport(dataset_id, dataset_name, 0.0, 0, warnings, errors, [], components)

        ordered = sorted(candles, key=lambda candle: candle.timestamp)
        timestamp_counts = Counter(candle.timestamp for candle in candles)
        duplicate_count = sum(count - 1 for count in timestamp_counts.values() if count > 1)
        if duplicate_count:
            warnings.append(
                QualityIssue(
                    "duplicate_candles",
                    "warning",
                    "Duplicate candle timestamps detected",
                    duplicate_count,
                )
            )
            components["duplicates"] = max(0.0, 100.0 - duplicate_count * 5.0)

        ordering_issues = sum(
            1
            for previous, current in zip(candles, candles[1:])
            if current.timestamp < previous.timestamp
        )
        if ordering_issues:
            errors.append(
                QualityIssue(
                    "timestamp_ordering",
                    "error",
                    "Candles are not chronologically ordered",
                    ordering_issues,
                )
            )
            components["ordering"] = max(0.0, 100.0 - ordering_issues * 10.0)

        bad_ohlc = 0
        mismatched_metadata = 0
        zero_volume = 0
        for candle in candles:
            if (
                min(candle.open, candle.high, candle.low, candle.close) <= 0
                or candle.high < max(candle.open, candle.close, candle.low)
                or candle.low > min(candle.open, candle.close, candle.high)
            ):
                bad_ohlc += 1
            if candle.symbol != symbol or candle.timeframe != timeframe:
                mismatched_metadata += 1
            if candle.volume == 0:
                zero_volume += 1

        if bad_ohlc:
            errors.append(QualityIssue("invalid_ohlc", "error", "Invalid OHLC values", bad_ohlc))
            components["ohlc"] = max(0.0, 100.0 - bad_ohlc * 20.0)
        if mismatched_metadata:
            errors.append(
                QualityIssue(
                    "metadata_mismatch",
                    "error",
                    "Symbol or timeframe mismatch detected",
                    mismatched_metadata,
                )
            )
            components["timeframe_consistency"] = max(0.0, 100.0 - mismatched_metadata * 10.0)
        if zero_volume:
            warnings.append(
                QualityIssue("zero_volume", "warning", "Zero-volume candles detected", zero_volume)
            )
            components["volume"] = max(0.0, 100.0 - zero_volume * 2.0)

        gaps = self.gap_detector.detect(ordered, timeframe)
        unexpected_gaps = [gap for gap in gaps if gap.severity != GapSeverity.EXPECTED]
        missing_intervals = sum(gap.missing_intervals for gap in unexpected_gaps)
        severe_gaps = sum(1 for gap in unexpected_gaps if gap.severity == GapSeverity.SEVERE)
        if unexpected_gaps:
            warnings.append(
                QualityIssue(
                    "unexpected_gaps",
                    "warning",
                    "Unexpected timestamp gaps detected",
                    len(unexpected_gaps),
                )
            )
            components["missing_data"] = max(
                0.0,
                100.0 - missing_intervals * 3.0 - severe_gaps * 10.0,
            )

        self._check_timeframe_delta(ordered, timeframe, warnings, components)
        score = round(sum(components.values()) / len(components), 2)
        if errors:
            score = min(score, 49.0)
        return QualityReport(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            quality_score=score,
            row_count=len(candles),
            warnings=warnings,
            errors=errors,
            gaps=gaps,
            components=components,
        )

    def _check_timeframe_delta(
        self,
        candles: list[Candle],
        timeframe: str,
        warnings: list[QualityIssue],
        components: dict[str, float],
    ) -> None:
        expected = parse_timeframe_seconds(timeframe)
        suspicious = 0
        for previous, current in zip(candles, candles[1:]):
            delta = int((current.timestamp - previous.timestamp).total_seconds())
            if delta > 0 and delta % expected != 0:
                suspicious += 1
        if suspicious:
            warnings.append(
                QualityIssue(
                    "timeframe_inconsistency",
                    "warning",
                    "Timestamp spacing is inconsistent with timeframe",
                    suspicious,
                )
            )
            components["timeframe_consistency"] = max(0.0, 100.0 - suspicious * 5.0)
