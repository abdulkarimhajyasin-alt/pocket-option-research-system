"""Storage writer and reader for research archive outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.research_archive.models import ResearchArchiveRecord, ResearchSnapshot, ResearchVersion


class ResearchArchiveStorage:
    """Persist archive snapshots, manifests, indexes, diffs, and evolution data."""

    def __init__(self, output_dir: Path | str = "storage/research_archive") -> None:
        self.output_dir = Path(output_dir)

    def ensure(self) -> None:
        (self.output_dir / "snapshots").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "diffs").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "evolution").mkdir(parents=True, exist_ok=True)

    def load_versions(self) -> list[dict[str, Any]]:
        return self._read_list(self.output_dir / "versions.json")

    def load_archive_index(self) -> list[dict[str, Any]]:
        return self._read_list(self.output_dir / "archive_index.json")

    def load_snapshot(self, version_label: str) -> dict[str, Any]:
        return self._read_dict(self.output_dir / "snapshots" / version_label / "snapshot.json")

    def save_archive(
        self,
        snapshot: ResearchSnapshot,
        version: ResearchVersion,
        diagnostics: list[dict[str, Any]],
        *,
        new_version: bool,
    ) -> ResearchArchiveRecord:
        self.ensure()
        version_dir = self.output_dir / "snapshots" / version.version_label
        version_dir.mkdir(parents=True, exist_ok=True)
        snapshot_payload = {**snapshot.to_dict(), "version": version.version_label}
        self._write(version_dir / "snapshot.json", snapshot_payload)
        self._write(version_dir / "source_manifest.json", snapshot.included_sources)
        self._write(version_dir / "safety_manifest.json", snapshot.safety_status)
        self._write(version_dir / "diagnostics.json", diagnostics)
        self._write(self.output_dir / "latest_snapshot.json", snapshot_payload)
        versions = self.load_versions()
        if new_version:
            versions.append(version.to_dict())
        self._write(self.output_dir / "versions.json", versions)
        record = ResearchArchiveRecord(
            archive_id=f"archive-{version.version_label}",
            version_id=version.version_id,
            snapshot_id=snapshot.snapshot_id,
            archive_path=str(version_dir),
            report_path=str(Path("reports") / "research_archive"),
            source_count=len(snapshot.included_sources),
            file_count=4,
            archive_status="stored",
            diagnostics_count=len(diagnostics),
        )
        index = self.load_archive_index()
        if new_version:
            index.append(record.to_dict())
        self._write(self.output_dir / "archive_index.json", index)
        return record

    def save_diff(self, name: str, payload: dict[str, Any]) -> Path:
        self.ensure()
        path = self.output_dir / "diffs" / name
        self._write(path, payload)
        return path

    def save_evolution(self, payload: dict[str, Any]) -> Path:
        self.ensure()
        path = self.output_dir / "evolution" / "evolution_report.json"
        self._write(path, payload)
        return path

    def _read_dict(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _read_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(payload, list):
            return []
        return [item for item in payload if isinstance(item, dict)]

    def _write(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
