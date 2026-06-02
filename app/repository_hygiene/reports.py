"""Report writer for repository hygiene outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RepositoryHygieneReportWriter:
    """Write hygiene report artifacts."""

    MAPPING = {
        "summary": "repository_hygiene_summary.json",
        "git_status_inventory": "git_status_inventory_report.json",
        "artifact_inventory": "artifact_inventory_report.json",
        "artifact_classification": "artifact_classification_report.json",
        "retention_policy": "retention_policy_report.json",
        "cleanup_plan": "cleanup_plan_report.json",
        "ignore_recommendations": "ignore_recommendations_report.json",
        "duplicate_artifacts": "duplicate_artifacts_report.json",
        "stale_artifacts": "stale_artifacts_report.json",
        "archive_policy": "archive_policy_report.json",
        "scorecard": "scorecard_report.json",
        "diagnostics": "diagnostics_report.json",
        "recommendations": "recommendations_report.json",
    }

    def __init__(self, output_dir: Path | str = "reports/repository_hygiene") -> None:
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
