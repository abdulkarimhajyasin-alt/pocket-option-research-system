"""Market-data ingestion validation for connector outputs."""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from loguru import logger

from app.data.models import CandleSeries


@dataclass
class DataValidationResult:
    """Structured data ingestion validation result."""

    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return True when no critical errors exist."""
        return not self.errors

    def add_warning(self, message: str) -> None:
        """Record a validation warning."""
        self.warnings.append(message)
        logger.bind(component="connectivity").warning("Data validation warning: {}", message)

    def add_error(self, message: str) -> None:
        """Record a critical validation error."""
        self.errors.append(message)
        logger.bind(component="connectivity").error("Data validation error: {}", message)

    def to_dict(self) -> dict[str, object]:
        """Return a serializable validation payload."""
        return {"passed": self.passed, "warnings": self.warnings, "errors": self.errors}


class ConnectorDataValidator:
    """Validates CandleSeries data returned by read-only connectors."""

    _timeframe_minutes = {"m1": 1, "1m": 1, "m5": 5, "5m": 5}

    def validate(
        self,
        series: CandleSeries,
        stale_after_minutes: int = 1440,
    ) -> DataValidationResult:
        """Validate candle schema, ordering, duplicates, gaps, and freshness."""
        result = DataValidationResult()
        if len(series) == 0:
            result.add_error("Candle series is empty")
            return result

        expected_delta = self._expected_delta(series.timeframe)
        seen = set()
        previous = None
        for candle in series:
            if candle.timestamp in seen:
                result.add_error(f"Duplicate candle timestamp: {candle.timestamp.isoformat()}")
            seen.add(candle.timestamp)
            if candle.high < max(candle.open, candle.close, candle.low):
                result.add_error(f"Invalid OHLC high at {candle.timestamp.isoformat()}")
            if candle.low > min(candle.open, candle.close, candle.high):
                result.add_error(f"Invalid OHLC low at {candle.timestamp.isoformat()}")
            if candle.timeframe != series.timeframe:
                result.add_error(f"Timeframe mismatch at {candle.timestamp.isoformat()}")
            if previous is not None:
                if candle.timestamp <= previous.timestamp:
                    result.add_error("Candle timestamps must be strictly increasing")
                elif expected_delta and candle.timestamp - previous.timestamp > expected_delta:
                    result.add_warning(f"Missing candle before {candle.timestamp.isoformat()}")
            previous = candle

        if series.last is not None:
            age = datetime.now(tz=UTC) - series.last.timestamp
            if age > timedelta(minutes=stale_after_minutes):
                result.add_warning(f"Stale data detected: last candle age {age}")
        logger.bind(component="connectivity").info("Data validation result: {}", result.to_dict())
        return result

    def _expected_delta(self, timeframe: str) -> timedelta | None:
        minutes = self._timeframe_minutes.get(timeframe.lower())
        return timedelta(minutes=minutes) if minutes else None
