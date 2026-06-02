"""Report writer for release baseline outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ReleaseBaselineReportWriter:
    """Write baseline report artifacts."""

    MAPPING = {
        "summary": "release_baseline_summary.json",
        "source_inventory": "source_inventory_report.json",
        "baseline_inventory": "baseline_inventory_report.json",
        "commit_classification": "commit_classification_report.json",
        "artifact_reconciliation": "artifact_reconciliation_report.json",
        "evidence_selection": "evidence_selection_report.json",
        "cleanup_checklist": "cleanup_checklist_report.json",
        "ignore_review": "ignore_review_report.json",
        "prompt_file_policy": "prompt_file_policy_report.json",
        "validation_churn": "validation_churn_report.json",
        "archive_reconciliation": "archive_reconciliation_report.json",
        "decision_matrix": "decision_matrix_report.json",
        "scorecard": "scorecard_report.json",
        "diagnostics": "diagnostics_report.json",
        "recommendations": "recommendations_report.json",
    }

    def __init__(self, output_dir: Path | str = "reports/release_baseline") -> None:
        self.output_dir = Path(output_dir)

    def export(self, payloads: dict[str, Any]) -> dict[str, str]:
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
