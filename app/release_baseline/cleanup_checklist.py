"""Manual cleanup checklist generation."""

from __future__ import annotations

from typing import Any

from app.release_baseline.models import CleanupChecklistItem, count_by
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS


class ManualCleanupChecklistEngine:
    """Build a non-destructive cleanup checklist."""

    def build(self, classifications: dict[str, Any]) -> dict[str, Any]:
        items = [
            self._item(index, item)
            for index, item in enumerate(classifications.get("items", []), start=1)
            if item.get("classification")
            in {
                "commit after review",
                "keep uncommitted",
                "ignore recommended",
                "manual cleanup candidate",
                "manual decision required",
                "excluded from baseline",
            }
        ]
        return {
            "items": items,
            "action_counts": count_by(items, "recommended_action"),
            **BASELINE_ONLY_FLAGS,
        }

    def _item(self, index: int, item: dict[str, Any]) -> dict[str, Any]:
        classification = str(item.get("classification", "manual decision required"))
        if classification == "manual cleanup candidate":
            action = "manual cleanup candidate"
            safety = "حساس"
            command = "Review path manually; no automatic command is provided."
        elif classification == "ignore recommended":
            action = "ignore proposal"
            safety = "يحتاج مراجعة"
            command = "Review .gitignore proposal manually."
        elif classification == "commit after review":
            action = "review"
            safety = "يحتاج مراجعة"
            command = "git diff -- <path>"
        elif classification == "excluded from baseline":
            action = "do not touch"
            safety = "ممنوع تلقائياً"
            command = ""
        else:
            action = "review"
            safety = "يحتاج مراجعة"
            command = "Review in IDE before baseline decision."
        return CleanupChecklistItem(
            item_id=f"BASE-CLEAN-{index:04d}",
            path=str(item.get("path", "")),
            issue=classification,
            recommended_action=action,
            reason=str(item.get("rationale", "Manual baseline review required.")),
            safety_level=safety,
            command_suggestion=command,
            destructive_action_forbidden=True,
            requires_human_confirmation=True,
        ).to_dict()
