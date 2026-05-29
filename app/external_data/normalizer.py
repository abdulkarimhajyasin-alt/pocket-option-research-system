"""Normalization utilities for read-only external market data."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.external_data.feed_errors import FeedValidationError
from app.external_data.models import NormalizedCandle, NormalizedTick, utc_now


class FeedNormalizer:
    """Convert provider-specific payloads into stable research models."""

    TIMEFRAME_ALIASES = {
        "m1": "1m",
        "1min": "1m",
        "1minute": "1m",
        "1": "1m",
        "m5": "5m",
        "5min": "5m",
        "5minute": "5m",
        "5": "5m",
        "h1": "1h",
        "1hour": "1h",
        "60": "1h",
    }

    def __init__(self, price_precision: int = 5) -> None:
        self.price_precision = price_precision

    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbols without assuming any broker-specific format."""
        return symbol.replace("/", "").replace("-", "").strip().upper()

    def normalize_timeframe(self, timeframe: str) -> str:
        """Normalize common timeframe aliases."""
        value = timeframe.strip().lower()
        return self.TIMEFRAME_ALIASES.get(value, value)

    def normalize_timestamp(self, value: datetime | str | int | float | None) -> datetime:
        """Normalize timestamp input to UTC."""
        if value is None:
            return utc_now()
        if isinstance(value, datetime):
            timestamp = value
        elif isinstance(value, (int, float)):
            timestamp = datetime.fromtimestamp(value, tz=UTC)
        elif isinstance(value, str):
            timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            raise FeedValidationError(f"Unsupported timestamp type: {type(value).__name__}")
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        return timestamp.astimezone(UTC)

    def normalize_price(self, value: float | int | str) -> float:
        """Normalize price precision."""
        return round(float(value), self.price_precision)

    def normalize_tick(
        self,
        payload: dict[str, Any],
        source: str,
        sequence: int = 0,
        received_at: datetime | None = None,
    ) -> NormalizedTick:
        """Normalize a raw tick dictionary."""
        received = self.normalize_timestamp(received_at)
        timestamp = self.normalize_timestamp(payload.get("timestamp") or payload.get("time"))
        latency = float(payload.get("latency_ms", (received - timestamp).total_seconds() * 1000))
        return NormalizedTick(
            symbol=self.normalize_symbol(str(payload["symbol"])),
            timestamp=timestamp,
            price=self.normalize_price(payload["price"]),
            source=source,
            bid=self._optional_price(payload.get("bid")),
            ask=self._optional_price(payload.get("ask")),
            volume=self._optional_float(payload.get("volume")),
            latency_ms=max(0.0, latency),
            sequence=int(payload.get("sequence", sequence)),
            received_at=received,
        )

    def normalize_candle(
        self,
        payload: dict[str, Any],
        source: str,
        sequence: int = 0,
        received_at: datetime | None = None,
    ) -> NormalizedCandle:
        """Normalize a raw candle dictionary."""
        received = self.normalize_timestamp(received_at)
        timestamp = self.normalize_timestamp(payload.get("timestamp") or payload.get("time"))
        latency = float(payload.get("latency_ms", (received - timestamp).total_seconds() * 1000))
        return NormalizedCandle(
            symbol=self.normalize_symbol(str(payload["symbol"])),
            timeframe=self.normalize_timeframe(str(payload["timeframe"])),
            timestamp=timestamp,
            open=self.normalize_price(payload["open"]),
            high=self.normalize_price(payload["high"]),
            low=self.normalize_price(payload["low"]),
            close=self.normalize_price(payload["close"]),
            source=source,
            volume=self._optional_float(payload.get("volume")),
            is_closed=bool(payload.get("is_closed", True)),
            latency_ms=max(0.0, latency),
            sequence=int(payload.get("sequence", sequence)),
            received_at=received,
        )

    def _optional_price(self, value: object) -> float | None:
        return None if value is None else self.normalize_price(value)  # type: ignore[arg-type]

    def _optional_float(self, value: object) -> float | None:
        return None if value is None else float(value)
