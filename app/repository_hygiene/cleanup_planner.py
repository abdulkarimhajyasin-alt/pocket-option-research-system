"""Non-destructive cleanup planning for repository hygiene."""

from __future__ import annotations

from typing import Any

from app.repository_hygiene.models import CleanupPlanItem
from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class CleanupPlanner:
    """Generate cleanup recommendations without deleting files."""

    def build(self, classifications: dict[str, Any], git_status: dict[str, Any]) -> dict[str, Any]:
        paths = {str(item.get("path")): item for item in classifications.get("items", [])}
        for item in git_status.get("items", []):
            paths.setdefault(
                str(item.get("path")),
                {
                    "path": item.get("path"),
                    "classification": item.get("category", "unknown"),
                    "reason": "Git status item requires hygiene review.",
                },
            )
        plan = [
            self._plan_item(index, item)
            for index, item in enumerate(paths.values(), start=1)
        ]
        return {"items": plan, **HYGIENE_ONLY_FLAGS}

    def _plan_item(self, index: int, item: dict[str, Any]) -> dict[str, Any]:
        classification = str(item.get("classification", "unknown"))
        path = str(item.get("path", ""))
        if classification in {"release artifact", "prompt artifact"}:
            action = "keep"
            safety = "آمن"
            manual = False
        elif classification in {"archive artifact", "generated retained"}:
            action = "review manually"
            safety = "يحتاج مراجعة"
            manual = True
        elif classification in {"cache artifact", "generated disposable"}:
            action = "eligible for manual cleanup"
            safety = "حساس"
            manual = True
        else:
            action = "review manually"
            safety = "يحتاج مراجعة"
            manual = True
        windows_note = ""
        if "research_archive" in path or "diff_" in path:
            windows_note = "Windows may deny cleanup due permissions or file attributes."
        return CleanupPlanItem(
            item_id=f"CLEAN-{index:04d}",
            path=path,
            classification=classification,
            recommended_action=action,
            safety_level=safety,
            requires_manual_review=manual,
            reason=str(item.get("reason", "Repository hygiene review item.")),
            windows_note=windows_note,
            destructive_action_forbidden=True,
        ).to_dict()
