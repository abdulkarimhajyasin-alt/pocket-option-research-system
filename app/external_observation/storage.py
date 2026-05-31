"""Storage for the external observation sandbox."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.external_observation.models import ExternalObservationResult


class ExternalObservationStorage:
    """Persist external observation sandbox outputs."""

    def __init__(self, output_dir: Path | str = "storage/external_observation") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: ExternalObservationResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "sandbox": self.output_dir / "sandbox_results.json",
            "sources": self.output_dir / "source_registry.json",
            "validation": self.output_dir / "validation_results.json",
            "monitoring": self.output_dir / "monitoring_results.json",
            "health": self.output_dir / "health_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["sandbox"], result.to_dict())
        self._write(paths["sources"], [item.to_dict() for item in result.sources])
        self._write(paths["validation"], result.validation.to_dict())
        self._write(paths["monitoring"], result.monitoring.to_dict())
        self._write(paths["health"], result.health.to_dict())
        self._write(paths["diagnostics"], analytics)
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
