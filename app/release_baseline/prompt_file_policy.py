"""Phase prompt file policy."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.release_baseline.models import PromptFilePolicyItem, count_by
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS


class PromptFilePolicyEngine:
    """Define handling rules for phase prompt files."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def build(self, sources: dict[str, Any]) -> dict[str, Any]:
        prompts = sorted(self.project_root.glob("phase*.md"))
        rows = [
            PromptFilePolicyItem(
                path=path.name,
                handling="commit after review",
                reason="Phase prompt is implementation evidence; do not delete automatically.",
            ).to_dict()
            for path in prompts
        ]
        deleted = [
            item
            for item in sources.get("git_status", {}).get("items", [])
            if item.get("status_label") == "deleted"
            and str(item.get("path", "")).startswith("phase")
        ]
        for item in deleted:
            rows.append(
                PromptFilePolicyItem(
                    path=str(item.get("path")),
                    handling="review deleted prompt",
                    reason="Deleted phase prompt requires human confirmation.",
                ).to_dict()
            )
        return {"items": rows, "handling_counts": count_by(rows, "handling"), **BASELINE_ONLY_FLAGS}
