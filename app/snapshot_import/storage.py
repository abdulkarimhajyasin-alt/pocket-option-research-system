"""Storage for manual snapshot imports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.snapshot_import.models import SnapshotImportResult


class SnapshotImportStorage:
    """Persist manual snapshot import outputs."""

    def __init__(self, output_dir: Path | str = "storage/snapshot_import") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: SnapshotImportResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "history": self.output_dir / "import_history.json",
            "registry": self.output_dir / "snapshot_registry.json",
            "validation": self.output_dir / "validation_results.json",
            "processing": self.output_dir / "processing_results.json",
            "quality": self.output_dir / "quality_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["history"], result.to_dict())
        self._write(paths["registry"], [item.to_dict() for item in result.imports])
        self._write(paths["validation"], result.validation.to_dict())
        self._write(paths["processing"], result.processing.to_dict())
        self._write(paths["quality"], result.quality.to_dict())
        self._write(paths["diagnostics"], analytics)
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
