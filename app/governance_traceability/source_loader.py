"""Load local traceability source artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.governance_traceability.schemas import TRACEABILITY_ONLY_FLAGS


class GovernanceTraceabilitySourceLoader:
    """Load optional local JSON sources without external calls."""

    SOURCE_GROUPS = {
        "production_system_design": (
            "storage/production_system_design",
            "reports/production_system_design",
        ),
        "operational_governance": (
            "storage/operational_governance",
            "reports/operational_governance",
        ),
        "trading_requirements": (
            "storage/trading_requirements",
            "reports/trading_requirements",
        ),
        "trading_architecture_program": (
            "storage/trading_architecture_program",
            "reports/trading_architecture_program",
        ),
    }

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def load(self) -> dict[str, Any]:
        inventory: dict[str, Any] = {"sources": {}, "missing_sources": []}
        for group, folders in self.SOURCE_GROUPS.items():
            files = []
            for folder in folders:
                root = self.project_root / folder
                if not root.exists():
                    inventory["missing_sources"].append(folder)
                    continue
                files.extend(self._read_folder(root))
            inventory["sources"][group] = {
                "file_count": len(files),
                "files": files,
                "available": bool(files),
            }
        inventory.update(TRACEABILITY_ONLY_FLAGS)
        return inventory

    def _read_folder(self, root: Path) -> list[dict[str, Any]]:
        files = []
        for path in sorted(root.glob("*.json")):
            files.append(
                {
                    "path": str(path),
                    "name": path.name,
                    "payload": self._read_json(path),
                }
            )
        return files

    def _read_json(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
