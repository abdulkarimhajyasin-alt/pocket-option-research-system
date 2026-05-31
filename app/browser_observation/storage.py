"""Storage for read-only browser observation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.browser_observation.models import BrowserObservationResult


class BrowserObservationStorage:
    """Persist read-only browser observation outputs."""

    def __init__(self, output_dir: Path | str = "storage/browser_observation") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: BrowserObservationResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "artifacts": self.output_dir / "artifact_registry.json",
            "adapter": self.output_dir / "adapter_results.json",
            "validation": self.output_dir / "validation_results.json",
            "visibility": self.output_dir / "visibility_results.json",
            "monitoring": self.output_dir / "monitoring_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["artifacts"], [item.to_dict() for item in result.artifacts])
        self._write(paths["adapter"], result.to_dict())
        self._write(paths["validation"], result.validation.to_dict())
        self._write(paths["visibility"], result.visibility.to_dict())
        self._write(paths["monitoring"], result.monitoring.to_dict())
        self._write(paths["diagnostics"], analytics)
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
