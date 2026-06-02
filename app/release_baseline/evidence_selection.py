"""Release evidence selection."""

from __future__ import annotations

from typing import Any

from app.release_baseline.models import ReleaseEvidenceItem, count_by
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS


class EvidenceSelectionEngine:
    """Select likely release evidence files for human review."""

    KEYWORDS = (
        "release_manifest",
        "certification",
        "summary",
        "safety",
        "readiness",
        "governance",
        "baseline",
    )

    def select(self, inventory: dict[str, Any]) -> dict[str, Any]:
        items = []
        for item in inventory.get("items", []):
            path = str(item.get("path", ""))
            if any(keyword in path for keyword in self.KEYWORDS):
                items.append(
                    ReleaseEvidenceItem(
                        path=path,
                        evidence_type=str(item.get("artifact_family", "baseline")),
                        evidence_value="Potential release baseline evidence.",
                        requires_human_review=True,
                    ).to_dict()
                )
        return {
            "items": items,
            "evidence_counts": count_by(items, "evidence_type"),
            **BASELINE_ONLY_FLAGS,
        }
