"""Dataset descriptors and candle split helpers."""

from __future__ import annotations

from pathlib import Path

from app.data.models import Candle, CandleSeries
from app.datasets.integrity import DatasetIntegrityVerifier
from app.validation.models import DatasetDescriptor


class DatasetManager:
    """Build reproducible dataset descriptors and deterministic slices."""

    def describe(
        self,
        candles: CandleSeries,
        name: str,
        source: Path | str,
        validation_splits: dict[str, object] | None = None,
    ) -> DatasetDescriptor:
        """Describe a candle series without storing raw candle data."""
        first = candles.first.timestamp if candles.first else None
        last = candles.last.timestamp if candles.last else None
        metadata = dict(validation_splits or {}).get("dataset_metadata", {})
        quality = dict(validation_splits or {}).get("dataset_quality", {})
        checksum = metadata.get("checksum") or DatasetIntegrityVerifier().checksum(tuple(candles))
        return DatasetDescriptor(
            name=name,
            source=str(source),
            symbol=candles.symbol,
            timeframe=candles.timeframe,
            start=first,
            end=last,
            sample_count=len(candles),
            validation_splits=dict(validation_splits or {}),
            dataset_id=metadata.get("dataset_id"),
            version=metadata.get("version"),
            checksum=checksum,
            quality_score=quality.get("quality_score"),
        )

    def slice(
        self,
        candles: CandleSeries,
        start_index: int,
        end_index: int,
    ) -> CandleSeries:
        """Return a half-open candle slice as a new series."""
        selected = list(candles[start_index:end_index])
        return CandleSeries(candles.symbol, candles.timeframe, selected)

    def from_rows(self, symbol: str, timeframe: str, rows: list[Candle]) -> CandleSeries:
        """Build a candle series from already normalized rows."""
        return CandleSeries(symbol, timeframe, rows)
