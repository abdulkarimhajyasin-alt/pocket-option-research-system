"""Storage for unified observation intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.observation_intelligence.models import ObservationIntelligenceResult


class ObservationIntelligenceStorage:
    """Persist unified observation intelligence outputs."""

    def __init__(self, output_dir: Path | str = "storage/observation_intelligence") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: ObservationIntelligenceResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "unified": self.output_dir / "unified_observations.json",
            "registry": self.output_dir / "observation_registry.json",
            "quality": self.output_dir / "quality_results.json",
            "confidence": self.output_dir / "confidence_results.json",
            "validation": self.output_dir / "validation_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["unified"], result.to_dict())
        self._write(paths["registry"], [item.to_dict() for item in result.observations])
        self._write(paths["quality"], result.quality.to_dict())
        self._write(paths["confidence"], result.confidence.to_dict())
        self._write(paths["validation"], result.validation.to_dict())
        self._write(paths["diagnostics"], analytics)
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
