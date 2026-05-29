"""Validation for read-only market stream events."""

from dataclasses import dataclass, field
from datetime import datetime

from app.streaming.models import MarketDataEvent, StreamEventType, normalize_timeframe, utc_now


@dataclass(frozen=True)
class StreamValidationResult:
    """Structured stream validation result."""

    valid: bool
    warnings: tuple[str, ...] = field(default_factory=tuple)
    critical_errors: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        """Return serializable validation diagnostics."""
        return {
            "valid": self.valid,
            "warnings": list(self.warnings),
            "critical_errors": list(self.critical_errors),
        }


class StreamValidator:
    """Validate ordering, staleness, prices, latency, and timeframe consistency."""

    def __init__(
        self,
        stale_after_seconds: float = 120.0,
        latency_warning_ms: float = 1_000.0,
        strict: bool = False,
    ) -> None:
        self.stale_after_seconds = stale_after_seconds
        self.latency_warning_ms = latency_warning_ms
        self.strict = strict
        self._last_key_by_symbol: dict[str, tuple[datetime, int]] = {}
        self._seen: set[tuple[str, int, str]] = set()

    def validate(
        self,
        event: MarketDataEvent,
        expected_timeframe: str | None = None,
        now: datetime | None = None,
    ) -> StreamValidationResult:
        """Validate one stream event."""
        warnings: list[str] = []
        errors: list[str] = []
        key = (event.source, event.sequence, event.event_id)
        symbol_key = f"{event.source}:{event.symbol}"

        if key in self._seen:
            errors.append("duplicate event")
        previous = self._last_key_by_symbol.get(symbol_key)
        current = (event.timestamp, event.sequence)
        if previous is not None and event.sequence < previous[1]:
            errors.append("out-of-order event")

        if event.latency_ms > self.latency_warning_ms:
            warnings.append("latency warning")
        current_time = now or utc_now()
        stale_seconds = (current_time - event.timestamp).total_seconds()
        if stale_seconds > self.stale_after_seconds:
            warnings.append("stale data")

        if event.event_type == StreamEventType.TICK and event.tick is not None:
            if event.tick.price <= 0:
                errors.append("invalid tick price")
        if event.event_type == StreamEventType.CANDLE and event.candle is not None:
            candle = event.candle
            if min(candle.open, candle.high, candle.low, candle.close) <= 0:
                errors.append("invalid candle price")
            if expected_timeframe and candle.timeframe != normalize_timeframe(expected_timeframe):
                errors.append("timeframe mismatch")

        if not errors:
            self._seen.add(key)
            self._last_key_by_symbol[symbol_key] = current
        if self.strict and warnings:
            errors.extend(warnings)
            warnings = []
        return StreamValidationResult(
            valid=not errors,
            warnings=tuple(warnings),
            critical_errors=tuple(errors),
        )
