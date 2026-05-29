"""Dataset version history management."""

from __future__ import annotations

from datetime import UTC, datetime

from app.datasets.models import DatasetMetadata, DatasetVersion


class DatasetVersionManager:
    """Track immutable version history for registered datasets."""

    def __init__(self) -> None:
        self._history: dict[str, list[DatasetVersion]] = {}

    def add_version(
        self,
        metadata: DatasetMetadata,
        quality_score: float,
        source_changes: str = "initial",
        quality_changes: str = "baseline",
        parent_version: str | None = None,
    ) -> DatasetVersion:
        """Add a dataset version record."""
        version = DatasetVersion(
            dataset_id=metadata.dataset_id,
            version=metadata.version,
            generated_at=datetime.now(UTC),
            checksum=metadata.checksum,
            row_count=metadata.row_count,
            source_changes=source_changes,
            quality_score=quality_score,
            quality_changes=quality_changes,
            parent_version=parent_version,
        )
        self._history.setdefault(metadata.dataset_id, []).append(version)
        return version

    def history(self, dataset_id: str) -> list[DatasetVersion]:
        """Return version history for a dataset."""
        return list(self._history.get(dataset_id, []))

    def compare(self, left: DatasetVersion, right: DatasetVersion) -> dict[str, object]:
        """Compare two dataset versions."""
        return {
            "dataset_id": left.dataset_id,
            "left_version": left.version,
            "right_version": right.version,
            "row_count_delta": right.row_count - left.row_count,
            "quality_delta": round(right.quality_score - left.quality_score, 4),
            "checksum_changed": left.checksum != right.checksum,
            "source_changes": right.source_changes,
            "quality_changes": right.quality_changes,
        }
