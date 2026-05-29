"""Gap detection for normalized research datasets."""

from __future__ import annotations

from datetime import datetime

from app.data.models import Candle
from app.datasets.models import GapRecord, GapSeverity
from app.datasets.utils import parse_timeframe_seconds


class GapDetector:
    """Detect expected and unexpected timestamp gaps."""

    def detect(self, candles: list[Candle] | tuple[Candle, ...], timeframe: str) -> list[GapRecord]:
        """Return timestamp gaps in chronological candle data."""
        if len(candles) < 2:
            return []
        expected_seconds = parse_timeframe_seconds(timeframe)
        ordered = sorted(candles, key=lambda candle: candle.timestamp)
        gaps: list[GapRecord] = []
        for previous, current in zip(ordered, ordered[1:]):
            actual_seconds = int((current.timestamp - previous.timestamp).total_seconds())
            if actual_seconds <= expected_seconds:
                continue
            missing = max(0, actual_seconds // expected_seconds - 1)
            severity, reason = self._classify(
                previous.timestamp,
                current.timestamp,
                expected_seconds,
                actual_seconds,
            )
            gaps.append(
                GapRecord(
                    start=previous.timestamp,
                    end=current.timestamp,
                    expected_seconds=expected_seconds,
                    actual_seconds=actual_seconds,
                    missing_intervals=missing,
                    severity=severity,
                    reason=reason,
                )
            )
        return gaps

    def _classify(
        self,
        start: datetime,
        end: datetime,
        expected_seconds: int,
        actual_seconds: int,
    ) -> tuple[GapSeverity, str]:
        if self._crosses_weekend(start, end):
            return GapSeverity.EXPECTED, "market_closure_weekend"
        if actual_seconds <= expected_seconds * 3:
            return GapSeverity.SUSPICIOUS, "short_unexpected_gap"
        return GapSeverity.SEVERE, "large_unexpected_gap"

    def _crosses_weekend(self, start: datetime, end: datetime) -> bool:
        current_day = start.date()
        end_day = end.date()
        while current_day <= end_day:
            if current_day.weekday() in {5, 6}:
                return True
            current_day = current_day.fromordinal(current_day.toordinal() + 1)
        return False
