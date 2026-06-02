"""Source loading for release baseline reconciliation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.release_baseline.schemas import BASELINE_ONLY_FLAGS
from app.repository_hygiene.git_status_parser import GitStatusParser


class BaselineSourceLoader:
    """Load local baseline sources without external calls."""

    SOURCE_GROUPS = {
        "repository_hygiene": (
            "storage/repository_hygiene",
            "reports/repository_hygiene",
        ),
        "release_packaging": (
            "storage/release_packaging",
            "reports/release_packaging",
        ),
        "platform_certification": (
            "storage/platform_certification",
            "reports/platform_certification",
        ),
        "review_board_simulation": (
            "storage/review_board_simulation",
            "reports/review_board_simulation",
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
        inventory["git_status"] = GitStatusParser(self.project_root).parse()
        inventory["phase_prompts"] = [
            path.name for path in sorted(self.project_root.glob("phase*.md"))
        ]
        inventory["gitignore_available"] = (self.project_root / ".gitignore").exists()
        inventory["readme_available"] = (self.project_root / "README.md").exists()
        inventory.update(BASELINE_ONLY_FLAGS)
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
