"""Research archive versioning engine."""

from __future__ import annotations

from pathlib import Path

from app.research_archive.models import CREATED_AT, ResearchSnapshot, ResearchVersion
from app.research_archive.schemas import VERSION_PREFIX, schema_metadata


class ResearchVersioningEngine:
    """Assign and track stable research archive versions."""

    def __init__(self, storage_dir: Path | str = "storage/research_archive") -> None:
        self.storage_dir = Path(storage_dir)

    def assign_version(
        self,
        snapshot: ResearchSnapshot,
        history: list[dict[str, object]],
        *,
        force: bool = False,
    ) -> tuple[ResearchVersion, bool]:
        """Return the next version or reuse latest when checksum is unchanged."""
        latest = history[-1] if history else None
        if latest and latest.get("checksum") == snapshot.checksum and not force:
            return self._from_dict(latest), False
        label = self.next_version_label(history)
        previous_id = str(latest.get("version_id")) if latest else None
        version = ResearchVersion(
            version_id=label,
            version_label=label,
            snapshot_id=snapshot.snapshot_id,
            created_at=CREATED_AT,
            previous_version_id=previous_id,
            checksum=snapshot.checksum,
            metadata={
                **schema_metadata(),
                "source_count": snapshot.source_summary.get("included_source_count", 0),
                "missing_source_count": snapshot.source_summary.get("missing_source_count", 0),
                "duplicate_checksum_reused": False,
            },
            safety_boundary=snapshot.safety_status,
        )
        return version, True

    def next_version_label(self, history: list[dict[str, object]]) -> str:
        return f"{VERSION_PREFIX}{len(history) + 1:04d}"

    def latest_version(self, history: list[dict[str, object]]) -> dict[str, object]:
        return history[-1] if history else {}

    def _from_dict(self, payload: dict[str, object]) -> ResearchVersion:
        return ResearchVersion(
            version_id=str(payload.get("version_id", "")),
            version_label=str(payload.get("version_label", "")),
            snapshot_id=str(payload.get("snapshot_id", "")),
            created_at=str(payload.get("created_at", CREATED_AT)),
            previous_version_id=payload.get("previous_version_id") or None,
            checksum=str(payload.get("checksum", "")),
            metadata=dict(payload.get("metadata", {})),
            safety_boundary=dict(payload.get("safety_boundary", {})),
        )
