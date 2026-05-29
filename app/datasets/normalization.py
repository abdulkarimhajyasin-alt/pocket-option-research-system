"""Dataset normalization helpers."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from app.data.models import Candle, CandleSeries
from app.data.normalizer import MarketDataNormalizer


class DatasetNormalizer:
    """Normalize dataset rows before quality analysis or validation."""

    COLUMN_ALIASES = {
        "time": "timestamp",
        "date": "timestamp",
        "o": "open",
        "h": "high",
        "l": "low",
        "c": "close",
        "vol": "volume",
    }

    def __init__(self, normalizer: MarketDataNormalizer | None = None) -> None:
        self.normalizer = normalizer or MarketDataNormalizer()

    def normalize_symbol(self, symbol: str) -> str:
        """Return broker-independent symbol spelling."""
        return symbol.strip().replace("/", "").replace("-", "").upper()

    def normalize_timeframe(self, timeframe: str) -> str:
        """Return platform timeframe spelling."""
        return self.normalizer.normalize_timeframe(timeframe)

    def normalize_timestamp(self, value: datetime | str) -> datetime:
        """Normalize timestamp to UTC."""
        if isinstance(value, datetime):
            timestamp = value
        else:
            timestamp = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        return timestamp.astimezone(UTC)

    def normalize_columns(self, row: dict[str, object]) -> dict[str, object]:
        """Normalize common OHLCV column aliases."""
        normalized: dict[str, object] = {}
        for key, value in row.items():
            cleaned = key.strip().lower()
            normalized[self.COLUMN_ALIASES.get(cleaned, cleaned)] = value
        return normalized

    def from_rows(
        self,
        rows: Iterable[dict[str, object]],
        symbol: str,
        timeframe: str,
    ) -> CandleSeries:
        """Build a normalized candle series from raw rows."""
        normalized_symbol = self.normalize_symbol(symbol)
        normalized_timeframe = self.normalize_timeframe(timeframe)
        candles = []
        for row in rows:
            item = self.normalize_columns(row)
            candles.append(
                Candle(
                    symbol=normalized_symbol,
                    timeframe=normalized_timeframe,
                    timestamp=self.normalize_timestamp(item["timestamp"]),
                    open=float(item["open"]),
                    high=float(item["high"]),
                    low=float(item["low"]),
                    close=float(item["close"]),
                    volume=float(item["volume"]) if item.get("volume") not in (None, "") else None,
                )
            )
        return self.normalizer.normalize_candles(normalized_symbol, normalized_timeframe, candles)
