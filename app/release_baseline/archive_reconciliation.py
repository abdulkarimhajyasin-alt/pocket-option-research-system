"""Archive artifact reconciliation."""

from __future__ import annotations

import re
from typing import Any

from app.release_baseline.models import ArchiveReconciliationItem, count_by
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS


class ArchiveReconciliationEngine:
    """Analyze research archive snapshots and diffs without cleanup."""

    def reconcile(self, inventory: dict[str, Any]) -> dict[str, Any]:
        archive_items = [
            item
            for item in inventory.get("items", [])
            if "archive" in str(item.get("file_category", ""))
            or "diff artifacts" == str(item.get("file_category", ""))
        ]
        versions = [self._version(str(item.get("path", ""))) for item in archive_items]
        latest = max([value for value in versions if value is not None], default=0)
        rows = [self._item(item, latest) for item in archive_items]
        return {
            "items": rows,
            "archive_counts": count_by(rows, "archive_classification"),
            "latest_version": latest,
            **BASELINE_ONLY_FLAGS,
        }

    def _item(self, item: dict[str, Any], latest: int) -> dict[str, Any]:
        path = str(item.get("path", ""))
        version = self._version(path)
        if version == latest and "snapshots" in path:
            classification = "latest archive snapshot"
            reason = "Latest archive snapshot should be reviewed as evidence."
        elif "diff_" in path and version and version >= max(0, latest - 1):
            classification = "release evidence snapshot"
            reason = "Recent diff may support release evidence."
        elif version and version < max(0, latest - 4):
            classification = "stale snapshot"
            reason = "Older archive artifact exceeds local retention window."
        elif "diff_" in path:
            classification = "transient diff"
            reason = "Diff artifact requires retention review."
        else:
            classification = "manual cleanup candidate"
            reason = "Archive artifact needs human reconciliation."
        return ArchiveReconciliationItem(
            path=path,
            archive_classification=classification,
            reason=reason,
        ).to_dict()

    def _version(self, path: str) -> int | None:
        matches = re.findall(r"research-v(\d+)", path)
        if not matches:
            return None
        return max(int(match) for match in matches)
