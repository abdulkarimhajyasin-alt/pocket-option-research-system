"""Comparison engine for read-only external feed samples."""

from dataclasses import dataclass, field
from datetime import datetime

from app.external_data.models import ExternalDataPayload, NormalizedCandle


@dataclass(frozen=True)
class FeedComparisonReport:
    """Comparison report for two external data sources."""

    source_a: str
    source_b: str
    matched: int
    timestamp_mismatches: int = 0
    candle_mismatches: int = 0
    latency_delta_ms: float = 0.0
    gap_delta: int = 0
    issues: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        """Return serializable comparison details."""
        return {
            "source_a": self.source_a,
            "source_b": self.source_b,
            "matched": self.matched,
            "timestamp_mismatches": self.timestamp_mismatches,
            "candle_mismatches": self.candle_mismatches,
            "latency_delta_ms": round(self.latency_delta_ms, 4),
            "gap_delta": self.gap_delta,
            "issues": list(self.issues),
        }


class FeedComparisonEngine:
    """Compare source A against source B using normalized payloads."""

    def __init__(self, timestamp_tolerance_ms: float = 250.0, price_tolerance: float = 0.0001):
        self.timestamp_tolerance_ms = timestamp_tolerance_ms
        self.price_tolerance = price_tolerance

    def compare(
        self,
        source_a: list[ExternalDataPayload],
        source_b: list[ExternalDataPayload],
    ) -> FeedComparisonReport:
        """Compare two feed samples by order, timestamp, candle values, latency, and gaps."""
        name_a = source_a[0].source if source_a else "source_a"
        name_b = source_b[0].source if source_b else "source_b"
        matched = min(len(source_a), len(source_b))
        timestamp_mismatches = 0
        candle_mismatches = 0
        issues: list[str] = []

        for left, right in zip(source_a, source_b, strict=False):
            if (
                self._timestamp_delta_ms(left.timestamp, right.timestamp)
                > self.timestamp_tolerance_ms
            ):
                timestamp_mismatches += 1
            if isinstance(left, NormalizedCandle) and isinstance(right, NormalizedCandle):
                if self._candle_delta_exceeded(left, right):
                    candle_mismatches += 1

        latency_a = self._average_latency(source_a)
        latency_b = self._average_latency(source_b)
        gap_delta = abs(self._gap_count(source_a) - self._gap_count(source_b))
        if timestamp_mismatches:
            issues.append("timestamp mismatch")
        if candle_mismatches:
            issues.append("candle mismatch")
        if gap_delta:
            issues.append("gap mismatch")
        return FeedComparisonReport(
            source_a=name_a,
            source_b=name_b,
            matched=matched,
            timestamp_mismatches=timestamp_mismatches,
            candle_mismatches=candle_mismatches,
            latency_delta_ms=abs(latency_a - latency_b),
            gap_delta=gap_delta,
            issues=tuple(issues),
        )

    def _timestamp_delta_ms(self, left: datetime, right: datetime) -> float:
        return abs((left - right).total_seconds() * 1000)

    def _candle_delta_exceeded(self, left: NormalizedCandle, right: NormalizedCandle) -> bool:
        return any(
            abs(getattr(left, field_name) - getattr(right, field_name)) > self.price_tolerance
            for field_name in ("open", "high", "low", "close")
        )

    def _average_latency(self, payloads: list[ExternalDataPayload]) -> float:
        if not payloads:
            return 0.0
        return sum(payload.latency_ms for payload in payloads) / len(payloads)

    def _gap_count(self, payloads: list[ExternalDataPayload]) -> int:
        gaps = 0
        previous: ExternalDataPayload | None = None
        for payload in payloads:
            if previous and (payload.timestamp - previous.timestamp).total_seconds() > 90:
                gaps += 1
            previous = payload
        return gaps
