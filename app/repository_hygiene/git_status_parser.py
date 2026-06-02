"""Safe git status parsing for repository hygiene."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

from app.repository_hygiene.models import GitStatusItem
from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class GitStatusParser:
    """Read and parse git status without mutating repository state."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def parse(self, text: str | None = None) -> dict[str, Any]:
        unavailable = False
        if text is None:
            try:
                completed = subprocess.run(
                    ("git", "status", "--porcelain"),
                    cwd=self.project_root,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                text = completed.stdout if completed.returncode == 0 else ""
                unavailable = completed.returncode != 0
            except (OSError, subprocess.TimeoutExpired):
                text = ""
                unavailable = True
        items = [self._parse_line(line) for line in text.splitlines() if line.strip()]
        return {
            "items": items,
            "summary": self._summary(items),
            "git_unavailable": unavailable,
            **HYGIENE_ONLY_FLAGS,
        }

    def parse_unavailable(self) -> dict[str, Any]:
        return {"items": [], "summary": {}, "git_unavailable": True, **HYGIENE_ONLY_FLAGS}

    def _parse_line(self, line: str) -> dict[str, Any]:
        index_status = line[0:1]
        worktree_status = line[1:2] if len(line) > 1 else " "
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        label = self._label(index_status, worktree_status)
        return GitStatusItem(
            path=path,
            index_status=index_status,
            worktree_status=worktree_status,
            status_label=label,
            category=self._category(path, label),
        ).to_dict()

    def _label(self, index_status: str, worktree_status: str) -> str:
        if index_status == "?" and worktree_status == "?":
            return "untracked"
        if index_status == "D" or worktree_status == "D":
            return "deleted"
        if index_status == "M" or worktree_status == "M":
            return "modified"
        if index_status == "A":
            return "added"
        return "other"

    def _category(self, path: str, label: str) -> str:
        normalized = path.replace("\\", "/")
        if normalized.startswith("reports/"):
            return "generated report change"
        if normalized.startswith("storage/research_archive/snapshots/"):
            return "archive snapshot"
        if normalized.startswith("storage/research_archive/diffs/"):
            return "diff artifact"
        if normalized.startswith("storage/"):
            return "generated storage change"
        if normalized.startswith(".pytest_cache/") or "__pycache__" in normalized:
            return "cache artifact"
        if normalized.startswith("phase") and normalized.endswith(".md"):
            return "prompt artifact"
        return label

    def _summary(self, items: list[dict[str, Any]]) -> dict[str, int]:
        counts = {"untracked": 0, "modified": 0, "deleted": 0, "added": 0, "other": 0}
        for item in items:
            label = str(item.get("status_label", "other"))
            counts[label] = counts.get(label, 0) + 1
        return counts
