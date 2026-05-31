"""Storage for architecture audit outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.architecture_audit.models import ArchitectureAuditRun


class ArchitectureAuditStorage:
    """Persist architecture audit outputs."""

    def __init__(self, output_dir: Path | str = "storage/architecture_audit") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: ArchitectureAuditRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "audit": self.output_dir / "audit_results.json",
            "consistency": self.output_dir / "consistency_results.json",
            "dependency": self.output_dir / "dependency_results.json",
            "performance": self.output_dir / "performance_results.json",
            "safety": self.output_dir / "safety_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["audit"], result.to_dict())
        self._write(paths["consistency"], result.consistency)
        self._write(paths["dependency"], result.dependency)
        self._write(paths["performance"], result.performance)
        self._write(paths["safety"], result.safety)
        self._write(paths["diagnostics"], result.to_dict())
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
