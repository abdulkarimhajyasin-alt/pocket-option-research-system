"""Storage for live observation replay outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.live_observation.models import LiveObservationResult


class LiveObservationStorage:
    """Persist latest replay outputs for downstream research."""

    def __init__(self, output_dir: Path | str = "storage/live_observation") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: LiveObservationResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "replay": self.output_dir / "replay_results.json",
            "timeline": self.output_dir / "timeline_results.json",
            "state": self.output_dir / "state_results.json",
            "quality": self.output_dir / "quality_results.json",
            "readiness": self.output_dir / "readiness_results.json",
            "validation": self.output_dir / "validation_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["replay"], result.replay.to_dict())
        self._write(paths["timeline"], result.timeline.to_dict())
        self._write(paths["state"], result.state.to_dict())
        self._write(paths["quality"], result.quality.to_dict())
        self._write(paths["readiness"], result.readiness.to_dict())
        self._write(paths["validation"], result.validation.to_dict())
        self._write(paths["diagnostics"], analytics)
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
