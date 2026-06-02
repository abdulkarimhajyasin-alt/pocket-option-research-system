"""Commit candidate classification."""

from __future__ import annotations

from typing import Any

from app.release_baseline.models import CommitClassification, count_by
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS


class CommitClassificationEngine:
    """Classify files for human baseline commit review."""

    def classify(self, inventory: dict[str, Any]) -> dict[str, Any]:
        items = [self._classify(item) for item in inventory.get("items", [])]
        return {
            "items": items,
            "classification_counts": count_by(items, "classification"),
            **BASELINE_ONLY_FLAGS,
        }

    def _classify(self, item: dict[str, Any]) -> dict[str, Any]:
        path = str(item.get("path", ""))
        category = str(item.get("file_category", "unknown"))
        family = str(item.get("artifact_family", ""))
        if path.startswith("app/release_baseline/") or path in {
            "scripts/run_release_baseline.py",
            "scripts/check_release_baseline.py",
            "tests/test_release_baseline.py",
        }:
            classification = "commit recommended"
            rationale = "Current phase source, script, or test artifact."
            review = False
        elif "release_baseline" in path:
            classification = "commit recommended"
            rationale = "Current phase generated baseline evidence."
            review = False
        elif category in {"source files", "scripts", "tests"}:
            classification = "commit after review"
            rationale = "Code or validation surface should be reviewed before commit."
            review = True
        elif family in {"release evidence artifacts", "certification artifacts"}:
            classification = "retain as release evidence"
            rationale = "Release or certification evidence has baseline value."
            review = True
        elif category in {"archive snapshots", "diff artifacts"}:
            classification = "manual cleanup candidate"
            rationale = "Archive churn needs explicit human retention decision."
            review = True
        elif category in {"generated reports", "generated storage files"}:
            classification = "manual decision required"
            rationale = "Generated validation churn should not be committed blindly."
            review = True
        elif category == "phase prompt files":
            classification = "commit after review"
            rationale = "Prompt files are implementation evidence."
            review = True
        else:
            classification = "excluded from baseline"
            rationale = "No baseline policy match."
            review = True
        return CommitClassification(
            path=path,
            classification=classification,
            rationale=rationale,
            requires_human_review=review,
        ).to_dict()
