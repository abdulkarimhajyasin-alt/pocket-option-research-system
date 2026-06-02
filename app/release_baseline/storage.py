"""Storage writer for release baseline outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ReleaseBaselineStorage:
    """Write baseline artifacts to local storage."""

    MAPPING = {
        "source_inventory": "source_inventory.json",
        "baseline_inventory": "baseline_inventory.json",
        "commit_classification": "commit_classification.json",
        "artifact_reconciliation": "artifact_reconciliation.json",
        "evidence_selection": "evidence_selection.json",
        "cleanup_checklist": "cleanup_checklist.json",
        "ignore_review": "ignore_review.json",
        "prompt_file_policy": "prompt_file_policy.json",
        "validation_churn": "validation_churn.json",
        "archive_reconciliation": "archive_reconciliation.json",
        "decision_matrix": "decision_matrix.json",
        "scorecard": "scorecard.json",
        "diagnostics": "diagnostics.json",
        "recommendations": "recommendations.json",
        "summary": "summary.json",
    }

    def __init__(self, output_dir: Path | str = "storage/release_baseline") -> None:
        self.output_dir = Path(output_dir)

    def save(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {}
        for key, filename in self.MAPPING.items():
            path = self.output_dir / filename
            path.write_text(
                json.dumps(payloads.get(key, {}), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            paths[key] = str(path)
        return paths
