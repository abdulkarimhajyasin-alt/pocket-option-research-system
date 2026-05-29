"""Feed quality analysis for normalized external market data."""

from __future__ import annotations

from datetime import datetime, timedelta

from app.external_data.models import (
    ExternalDataPayload,
    FeedLatencyMetrics,
    FeedQualityMetrics,
    NormalizedCandle,
    utc_now,
)


class FeedQualityAnalyzer:
    """Detect stale data, missing data, duplicates, ordering issues, latency, and gaps."""

    def __init__(
        self,
        stale_after_seconds: float = 120.0,
        latency_warning_ms: float = 1_000.0,
        expected_interval_seconds: float | None = 60.0,
    ) -> None:
        self.stale_after_seconds = stale_after_seconds
        self.latency_warning_ms = latency_warning_ms
        self.expected_interval_seconds = expected_interval_seconds

    def analyze(
        self,
        payloads: list[ExternalDataPayload],
        now: datetime | None = None,
    ) -> FeedQualityMetrics:
        """Return feed quality metrics for a payload sample."""
        current_time = now or utc_now()
        issues: list[str] = []
        seen: set[tuple[str, str, datetime, int]] = set()
        stale_count = duplicate_count = ordering_count = gap_count = latency_count = 0
        previous_by_key: dict[tuple[str, str], ExternalDataPayload] = {}

        for payload in payloads:
            kind = "candle" if isinstance(payload, NormalizedCandle) else "tick"
            unique_key = (payload.source, payload.symbol, payload.timestamp, payload.sequence)
            if unique_key in seen:
                duplicate_count += 1
            seen.add(unique_key)

            if (current_time - payload.timestamp).total_seconds() > self.stale_after_seconds:
                stale_count += 1
            if payload.latency_ms > self.latency_warning_ms:
                latency_count += 1

            series_key = (payload.source, f"{payload.symbol}:{kind}")
            previous = previous_by_key.get(series_key)
            if previous is not None and payload.timestamp < previous.timestamp:
                ordering_count += 1
            if (
                previous is not None
                and self.expected_interval_seconds
                and isinstance(payload, NormalizedCandle)
                and isinstance(previous, NormalizedCandle)
            ):
                expected = timedelta(seconds=self.expected_interval_seconds)
                if payload.timestamp - previous.timestamp > expected * 1.5:
                    gap_count += 1
            previous_by_key[series_key] = payload

        missing_count = 1 if not payloads else 0
        penalties = (
            stale_count * 8
            + missing_count * 15
            + duplicate_count * 10
            + ordering_count * 12
            + gap_count * 10
            + latency_count * 5
        )
        score = max(0.0, 100.0 - penalties)
        if stale_count:
            issues.append("stale data")
        if missing_count:
            issues.append("missing data")
        if duplicate_count:
            issues.append("duplicates")
        if ordering_count:
            issues.append("ordering issues")
        if gap_count:
            issues.append("gaps")
        if latency_count:
            issues.append("latency warnings")
        return FeedQualityMetrics(
            sample_count=len(payloads),
            stale_count=stale_count,
            missing_count=missing_count,
            duplicate_count=duplicate_count,
            ordering_issue_count=ordering_count,
            gap_count=gap_count,
            latency_warning_count=latency_count,
            quality_score=score,
            issues=tuple(issues),
        )

    def latency_metrics(self, payloads: list[ExternalDataPayload]) -> FeedLatencyMetrics:
        """Build latency metrics for a payload sample."""
        samples = [payload.latency_ms for payload in payloads]
        if not samples:
            return FeedLatencyMetrics(threshold_ms=self.latency_warning_ms)
        return FeedLatencyMetrics(
            sample_count=len(samples),
            average_ms=sum(samples) / len(samples),
            maximum_ms=max(samples),
            latest_ms=samples[-1],
            threshold_ms=self.latency_warning_ms,
        )
