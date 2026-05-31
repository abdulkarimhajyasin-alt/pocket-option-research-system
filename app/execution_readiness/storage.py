"""Storage for execution readiness outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.execution_readiness.models import ExecutionReadinessRun


class ExecutionReadinessStorage:
    """Persist research-only execution readiness outputs."""

    def __init__(self, output_dir: Path | str = "storage/execution_readiness") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: ExecutionReadinessRun, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "execution_candidates": self.output_dir / "execution_candidates.json",
            "readiness_results": self.output_dir / "readiness_results.json",
            "qualification_results": self.output_dir / "qualification_results.json",
            "gate_results": self.output_dir / "gate_results.json",
            "validation_results": self.output_dir / "validation_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["execution_candidates"], [item.to_dict() for item in result.candidates])
        self._write(paths["readiness_results"], result.readiness.to_dict())
        self._write(paths["qualification_results"], result.qualification.to_dict())
        self._write(paths["gate_results"], [item.to_dict() for item in result.gates])
        self._write(paths["validation_results"], result.validation.to_dict())
        self._write(paths["diagnostics"], analytics)
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
