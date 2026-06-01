"""Storage writer for governance traceability outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class GovernanceTraceabilityStorage:
    """Write traceability artifacts to local storage."""

    def __init__(self, output_dir: Path | str = "storage/governance_traceability") -> None:
        self.output_dir = Path(output_dir)

    def save(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "source_inventory": "source_inventory.json",
            "control_mappings": "control_mappings.json",
            "control_matrix": "control_matrix.json",
            "evidence_matrix": "evidence_matrix.json",
            "readiness_mapping": "readiness_mapping.json",
            "risk_mapping": "risk_mapping.json",
            "incident_mapping": "incident_mapping.json",
            "release_mapping": "release_mapping.json",
            "monitoring_mapping": "monitoring_mapping.json",
            "policy_mapping": "policy_mapping.json",
            "coverage_summary": "coverage_summary.json",
            "diagnostics": "diagnostics.json",
            "recommendations": "recommendations.json",
            "summary": "summary.json",
        }
        paths = {}
        for key, filename in mapping.items():
            path = self.output_dir / filename
            path.write_text(
                json.dumps(payloads.get(key, {}), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            paths[key] = str(path)
        return paths
