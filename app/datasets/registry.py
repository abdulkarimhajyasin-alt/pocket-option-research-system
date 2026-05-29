"""Centralized research dataset registry."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

from app.data.models import CandleSeries
from app.datasets.integrity import DatasetIntegrityVerifier
from app.datasets.models import DatasetMetadata


class DatasetRegistry:
    """Register and retrieve immutable dataset metadata."""

    def __init__(self, verifier: DatasetIntegrityVerifier | None = None) -> None:
        self.verifier = verifier or DatasetIntegrityVerifier()
        self._datasets: dict[str, DatasetMetadata] = {}

    def register(
        self,
        dataset_name: str,
        source: Path | str,
        candles: CandleSeries,
        version: str = "v1",
        tags: tuple[str, ...] = (),
    ) -> DatasetMetadata:
        """Register a dataset and reject duplicate ID collisions."""
        checksum = self.verifier.checksum(tuple(candles))
        dataset_id = self.build_dataset_id(
            dataset_name, str(source), candles.symbol, candles.timeframe
        )
        if dataset_id in self._datasets:
            existing = self._datasets[dataset_id]
            if existing.checksum != checksum or existing.version != version:
                raise ValueError(
                    f"Dataset ID already registered with different metadata: {dataset_id}"
                )
            return existing
        metadata = DatasetMetadata(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            source=str(source),
            symbol=candles.symbol,
            timeframe=candles.timeframe,
            start_time=candles.first.timestamp if candles.first else None,
            end_time=candles.last.timestamp if candles.last else None,
            row_count=len(candles),
            checksum=checksum,
            version=version,
            tags=tags,
        )
        self._datasets[dataset_id] = metadata
        return metadata

    def get(self, dataset_id: str) -> DatasetMetadata:
        """Return metadata by dataset ID."""
        return self._datasets[dataset_id]

    def list(self) -> list[DatasetMetadata]:
        """List available datasets."""
        return sorted(self._datasets.values(), key=lambda item: item.dataset_id)

    def build_version_record(
        self, metadata: DatasetMetadata, quality_score: float
    ) -> dict[str, object]:
        """Return a version record payload for reporting."""
        return {
            "dataset_id": metadata.dataset_id,
            "version": metadata.version,
            "generated_at": datetime.now(UTC).isoformat(),
            "checksum": metadata.checksum,
            "row_count": metadata.row_count,
            "quality_score": quality_score,
        }

    def build_dataset_id(self, name: str, source: str, symbol: str, timeframe: str) -> str:
        """Build deterministic dataset ID from stable metadata."""
        value = f"{name}|{source}|{symbol}|{timeframe}"
        return str(uuid5(NAMESPACE_URL, value))
