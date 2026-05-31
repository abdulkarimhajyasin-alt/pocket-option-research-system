"""Storage for paper control center outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.paper_control_center.models import PaperControlCenterRun


class PaperControlStorage:
    """Persist paper control center outputs."""

    def __init__(self, output_dir: Path | str = "storage/paper_control_center") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: PaperControlCenterRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "control_center": self.output_dir / "control_center_results.json",
            "health": self.output_dir / "health_results.json",
            "monitoring": self.output_dir / "monitoring_results.json",
            "governance": self.output_dir / "governance_results.json",
            "decision": self.output_dir / "decision_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["control_center"], result.control.to_dict())
        self._write(paths["health"], result.health)
        self._write(paths["monitoring"], result.monitoring)
        self._write(paths["governance"], [item.to_dict() for item in result.governance])
        self._write(paths["decision"], result.decision)
        self._write(paths["diagnostics"], result.to_dict())
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
