"""Report writer for governance traceability outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class GovernanceTraceabilityReportWriter:
    """Write traceability report artifacts."""

    def __init__(self, output_dir: Path | str = "reports/governance_traceability") -> None:
        self.output_dir = Path(output_dir)

    def export(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "summary": "governance_traceability_summary.json",
            "source_inventory": "source_inventory_report.json",
            "control_mappings": "control_mappings_report.json",
            "control_matrix": "control_matrix_report.json",
            "evidence_matrix": "evidence_matrix_report.json",
            "readiness_mapping": "readiness_mapping_report.json",
            "risk_mapping": "risk_mapping_report.json",
            "incident_mapping": "incident_mapping_report.json",
            "release_mapping": "release_mapping_report.json",
            "monitoring_mapping": "monitoring_mapping_report.json",
            "policy_mapping": "policy_mapping_report.json",
            "coverage_summary": "coverage_summary_report.json",
            "diagnostics": "diagnostics_report.json",
            "recommendations": "recommendations_report.json",
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
