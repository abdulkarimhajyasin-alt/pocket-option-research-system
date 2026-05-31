"""Manual snapshot import registration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.snapshot_import.models import SUPPORTED_IMPORT_TYPES
from app.snapshot_import.models import SnapshotImport


class SnapshotImporter:
    """Register manually provided files from the local upload directory."""

    def __init__(
        self,
        project_root: Path | str = ".",
        upload_dir: Path | str = "storage/snapshot_import/uploads",
        max_size_bytes: int = 2_000_000,
    ) -> None:
        self.project_root = Path(project_root)
        self.upload_dir = self.project_root / upload_dir
        self.max_size_bytes = max_size_bytes

    def register_uploads(self) -> tuple[SnapshotImport, ...]:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self._seed_sample_if_empty()
        imports = [
            self._register_file(path)
            for path in sorted(self.upload_dir.iterdir())
            if path.is_file()
        ]
        return tuple(imports)

    def safe_upload_path(self, filename: str) -> Path:
        """Return a safe path inside the manual upload directory."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(filename).name.replace(" ", "_")
        if not safe_name:
            safe_name = "snapshot.txt"
        return self.upload_dir / safe_name

    def _register_file(self, path: Path) -> SnapshotImport:
        import_type = self._type_for_path(path)
        readable = self._is_readable(path)
        size = path.stat().st_size
        valid = (
            readable
            and import_type in SUPPORTED_IMPORT_TYPES
            and 0 < size <= self.max_size_bytes
        )
        return SnapshotImport(
            import_id=path.stem,
            filename=path.name,
            import_type=import_type,
            source_path=str(path),
            imported_at=str(path.stat().st_mtime_ns),
            size_bytes=size,
            validation_status="ناجح" if valid else "تحذير",
            processing_status="جاهز" if valid else "يحتاج مراجعة",
            metadata={
                "manual_upload": True,
                "readable": readable,
                "extension": path.suffix.lower(),
                "max_size_bytes": self.max_size_bytes,
            },
        )

    def _type_for_path(self, path: Path) -> str:
        suffix = path.suffix.lower()
        name = path.name.lower()
        if suffix == ".html":
            return "html_snapshot"
        if suffix == ".json":
            return "json_snapshot"
        if "dom" in name:
            return "dom_export"
        if "capture" in name:
            return "page_capture"
        if "dump" in name:
            return "observation_dump"
        return "static_snapshot"

    def _is_readable(self, path: Path) -> bool:
        try:
            if path.suffix.lower() == ".json":
                payload: Any = json.loads(path.read_text(encoding="utf-8"))
                return isinstance(payload, (dict, list))
            return bool(path.read_text(encoding="utf-8").strip())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return False

    def _seed_sample_if_empty(self) -> None:
        if any(self.upload_dir.iterdir()):
            return
        sample = self.upload_dir / "manual_sample_snapshot.json"
        payload = {
            "asset": "EURUSD",
            "symbol": "EURUSD",
            "payout": 82,
            "session": "research",
            "timestamp": "sample",
            "market": {"open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15},
            "manual_only": True,
        }
        sample.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
