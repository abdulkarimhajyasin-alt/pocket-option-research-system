"""Archive package orchestration."""

from __future__ import annotations

from pathlib import Path

from app.research_archive.models import ResearchArchiveRecord, ResearchSnapshot, ResearchVersion
from app.research_archive.storage import ResearchArchiveStorage


class ResearchArchiveEngine:
    """Persist complete research archive packages."""

    def __init__(self, storage: ResearchArchiveStorage | None = None) -> None:
        self.storage = storage or ResearchArchiveStorage()

    def persist(
        self,
        snapshot: ResearchSnapshot,
        version: ResearchVersion,
        diagnostics: list[dict[str, object]],
        *,
        new_version: bool,
    ) -> ResearchArchiveRecord:
        return self.storage.save_archive(
            snapshot,
            version,
            diagnostics,
            new_version=new_version,
        )

    def expected_package_paths(self, version_label: str) -> list[Path]:
        base = self.storage.output_dir / "snapshots" / version_label
        return [
            base / "snapshot.json",
            base / "source_manifest.json",
            base / "safety_manifest.json",
            base / "diagnostics.json",
        ]
