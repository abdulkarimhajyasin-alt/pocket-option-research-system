"""CSV loader for historical candle data."""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from pathlib import Path

from loguru import logger

from app.data.models import Candle, CandleSeries
from app.data.normalizer import MarketDataNormalizer


class CsvCandleLoader:
    """Loads historical OHLCV candles from CSV files."""

    REQUIRED_COLUMNS = {"timestamp", "open", "high", "low", "close", "volume"}

    def __init__(self, normalizer: MarketDataNormalizer | None = None) -> None:
        self.normalizer = normalizer or MarketDataNormalizer()

    def load(self, path: Path | str, symbol: str, timeframe: str) -> CandleSeries:
        """Load, validate, normalize, and sort candles from a CSV file."""
        csv_path = Path(path)
        logger.info("Loading historical candles from {}", csv_path)

        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            self._validate_columns(reader.fieldnames)
            candles = self._read_rows(reader, symbol, timeframe)

        series = self.normalizer.normalize_candles(symbol, timeframe, candles)
        logger.info("Loaded {} valid candles from {}", len(series), csv_path)
        return series

    def _validate_columns(self, fieldnames: list[str] | None) -> None:
        if fieldnames is None:
            raise ValueError("CSV file is missing a header row")

        missing = self.REQUIRED_COLUMNS.difference(fieldnames)
        if missing:
            raise ValueError(f"CSV file is missing required columns: {sorted(missing)}")

    def _read_rows(
        self,
        reader: csv.DictReader,
        symbol: str,
        timeframe: str,
    ) -> list[Candle]:
        candles: list[Candle] = []
        normalized_timeframe = self.normalizer.normalize_timeframe(timeframe)

        for row_number, row in enumerate(reader, start=2):
            try:
                candles.append(self._row_to_candle(row, symbol, normalized_timeframe))
            except (TypeError, ValueError) as exc:
                logger.warning("Skipping invalid CSV row {}: {}", row_number, exc)

        return candles

    def _row_to_candle(self, row: dict[str, str], symbol: str, timeframe: str) -> Candle:
        timestamp = self._parse_timestamp(row["timestamp"])
        volume_text = row.get("volume", "").strip()
        volume = float(volume_text) if volume_text else None

        return Candle(
            symbol=symbol.upper(),
            timeframe=timeframe,
            timestamp=timestamp,
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=volume,
        )

    def _parse_timestamp(self, value: str) -> datetime:
        cleaned = value.strip().replace("Z", "+00:00")
        timestamp = datetime.fromisoformat(cleaned)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        return timestamp.astimezone(UTC)
