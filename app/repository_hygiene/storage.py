"""Storage writer for repository hygiene outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RepositoryHygieneStorage:
    """Write hygiene artifacts to local storage."""

    MAPPING = {
        "git_status_inventory": "git_status_inventory.json",
        "artifact_inventory": "artifact_inventory.json",
        "artifact_classification": "artifact_classification.json",
        "retention_policy": "retention_policy.json",
        "cleanup_plan": "cleanup_plan.json",
        "ignore_recommendations": "ignore_recommendations.json",
        "duplicate_artifacts": "duplicate_artifacts.json",
        "stale_artifacts": "stale_artifacts.json",
        "archive_policy": "archive_policy.json",
        "scorecard": "scorecard.json",
        "diagnostics": "diagnostics.json",
        "recommendations": "recommendations.json",
        "summary": "summary.json",
    }

    def __init__(self, output_dir: Path | str = "storage/repository_hygiene") -> None:
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
