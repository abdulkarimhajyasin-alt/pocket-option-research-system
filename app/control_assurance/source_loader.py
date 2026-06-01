"""Load local assurance source artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.control_assurance.schemas import ASSURANCE_ONLY_FLAGS


class ControlAssuranceSourceLoader:
    """Load optional local JSON sources without external calls."""

    SOURCE_GROUPS = {
        "operational_governance": (
            "storage/operational_governance",
            "reports/operational_governance",
        ),
        "governance_traceability": (
            "storage/governance_traceability",
            "reports/governance_traceability",
        ),
        "production_system_design": (
            "storage/production_system_design",
            "reports/production_system_design",
        ),
        "trading_requirements": (
            "storage/trading_requirements",
            "reports/trading_requirements",
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
        inventory.update(ASSURANCE_ONLY_FLAGS)
        return inventory

    def _read_folder(self, root: Path) -> list[dict[str, Any]]:
        return [
            {"path": str(path), "name": path.name, "payload": self._read_json(path)}
            for path in sorted(root.glob("*.json"))
        ]

    def _read_json(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
