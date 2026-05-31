"""Storage for paper-to-live readiness outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.paper_live_readiness.models import PaperToLiveReadinessRun


class PaperToLiveReadinessStorage:
    """Persist readiness gate outputs."""

    def __init__(self, output_dir: Path | str = "storage/paper_live_readiness") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: PaperToLiveReadinessRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "readiness": self.output_dir / "readiness_results.json",
            "gates": self.output_dir / "gate_results.json",
            "safety": self.output_dir / "safety_results.json",
            "maturity": self.output_dir / "maturity_results.json",
            "stability": self.output_dir / "stability_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["readiness"], result.readiness.to_dict())
        self._write(paths["gates"], [item.to_dict() for item in result.gates])
        self._write(paths["safety"], result.safety)
        self._write(paths["maturity"], result.maturity)
        self._write(paths["stability"], result.stability)
        self._write(paths["diagnostics"], result.to_dict())
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
