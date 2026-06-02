"""Generated artifact inventory for repository hygiene."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from app.repository_hygiene.models import ArtifactClassification, ArtifactInventoryItem
from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class ArtifactInventoryEngine:
    """Inventory local artifacts without modifying them."""

    ROOTS = ("reports", "storage")

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def inventory(self) -> dict[str, Any]:
        items = []
        for root_name in self.ROOTS:
            root = self.project_root / root_name
            if not root.exists():
                continue
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    items.append(self._item(path))
        for path in sorted(self.project_root.glob("phase*.md")):
            if path.is_file():
                items.append(self._item(path))
        return {"items": items, "summary": self._summary(items), **HYGIENE_ONLY_FLAGS}

    def classify(self, inventory: dict[str, Any]) -> dict[str, Any]:
        items = [
            self._classification(str(item.get("path", "")))
            for item in inventory.get("items", [])
        ]
        counts: dict[str, int] = {}
        for item in items:
            key = str(item.get("classification", "unknown"))
            counts[key] = counts.get(key, 0) + 1
        return {"items": items, "classification_counts": counts, **HYGIENE_ONLY_FLAGS}

    def _item(self, path: Path) -> dict[str, Any]:
        relative = path.relative_to(self.project_root).as_posix()
        match = re.search(r"research-v(\d+)", relative)
        version = int(match.group(1)) if match else None
        return ArtifactInventoryItem(
            path=relative,
            artifact_family=self._family(relative),
            file_name=path.name,
            suffix=path.suffix,
            size_bytes=path.stat().st_size,
            version_number=version,
        ).to_dict()

    def _classification(self, path: str) -> dict[str, Any]:
        if path.startswith("reports/release_packaging/"):
            classification = "release artifact"
            reason = "Release evidence should be retained."
            candidate = True
        elif path.startswith("reports/") and "certification" in path:
            classification = "release artifact"
            reason = "Certification evidence should be retained."
            candidate = True
        elif path.startswith("storage/research_archive/"):
            classification = "archive artifact"
            reason = "Research archive evidence requires retention policy review."
            candidate = True
        elif path.startswith("reports/") or path.startswith("storage/"):
            classification = "generated retained"
            reason = "Generated local research artifact."
            candidate = False
        elif path.startswith("phase") and path.endswith(".md"):
            classification = "prompt artifact"
            reason = "Phase prompt file."
            candidate = True
        elif "__pycache__" in path or ".pytest_cache" in path:
            classification = "cache artifact"
            reason = "Local cache artifact."
            candidate = False
        else:
            classification = "unknown"
            reason = "No explicit artifact policy match."
            candidate = False
        return ArtifactClassification(
            path=path,
            classification=classification,
            reason=reason,
            source_control_candidate=candidate,
        ).to_dict()

    def _family(self, path: str) -> str:
        if "research_archive/snapshots" in path:
            return "archive snapshot"
        if "research_archive/diffs" in path:
            return "diff artifact"
        if path.startswith("reports/"):
            return "report artifact"
        if path.startswith("storage/"):
            return "storage artifact"
        if path.startswith("phase") and path.endswith(".md"):
            return "prompt artifact"
        return "unknown"

    def _summary(self, items: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            family = str(item.get("artifact_family", "unknown"))
            counts[family] = counts.get(family, 0) + 1
        return counts
