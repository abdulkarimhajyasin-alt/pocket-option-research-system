"""Release baseline inventory builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.release_baseline.models import BaselineInventoryItem, count_by
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS


class BaselineInventoryEngine:
    """Build a local release baseline inventory."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def build(self, sources: dict[str, Any]) -> dict[str, Any]:
        items: dict[str, dict[str, Any]] = {}
        for status in sources.get("git_status", {}).get("items", []):
            path = str(status.get("path", ""))
            items[path] = self._item(
                path,
                source="git-status",
                git_status=str(status.get("status_label", "")),
            )
        for root in ("app", "scripts", "tests", "reports", "storage"):
            base = self.project_root / root
            if not base.exists():
                continue
            for path in sorted(base.rglob("*")):
                if path.is_file():
                    relative = path.relative_to(self.project_root).as_posix()
                    items.setdefault(relative, self._item(relative, source=root))
        for path in sorted(self.project_root.glob("phase*.md")):
            relative = path.name
            items.setdefault(relative, self._item(relative, source="phase-prompt"))
        rows = list(items.values())
        return {
            "items": rows,
            "category_counts": count_by(rows, "file_category"),
            **BASELINE_ONLY_FLAGS,
        }

    def _item(self, path: str, source: str, git_status: str = "") -> dict[str, Any]:
        return BaselineInventoryItem(
            path=path,
            source=source,
            file_category=self._category(path),
            git_status=git_status,
            artifact_family=self._family(path),
        ).to_dict()

    def _category(self, path: str) -> str:
        if path.startswith("app/"):
            return "source files"
        if path.startswith("scripts/"):
            return "scripts"
        if path.startswith("tests/"):
            return "tests"
        if path.startswith("reports/"):
            return "generated reports"
        if path.startswith("storage/research_archive/snapshots/"):
            return "archive snapshots"
        if path.startswith("storage/research_archive/diffs/"):
            return "diff artifacts"
        if path.startswith("storage/"):
            return "generated storage files"
        if path.startswith("phase") and path.endswith(".md"):
            return "phase prompt files"
        return "unknown"

    def _family(self, path: str) -> str:
        if "release_packaging" in path:
            return "release evidence artifacts"
        if "platform_certification" in path:
            return "certification artifacts"
        if "repository_hygiene" in path:
            return "current hygiene outputs"
        if "release_baseline" in path:
            return "current phase artifacts"
        if "research_archive" in path:
            return "archive artifacts"
        if path.startswith("reports/") or path.startswith("storage/"):
            return "validation artifact handling"
        return "baseline source"
