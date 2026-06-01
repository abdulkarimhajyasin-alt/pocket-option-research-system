"""Report writer for operational governance outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class OperationalGovernanceReportWriter:
    """Write governance report artifacts."""

    def __init__(self, output_dir: Path | str = "reports/operational_governance") -> None:
        self.output_dir = Path(output_dir)

    def export(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "summary": "operational_governance_summary.json",
            "authority_model": "authority_model_report.json",
            "approval_workflows": "approval_workflows_report.json",
            "change_management": "change_management_report.json",
            "release_governance": "release_governance_report.json",
            "incident_escalation": "incident_escalation_report.json",
            "kill_switch_governance": "kill_switch_governance_report.json",
            "audit_controls": "audit_controls_report.json",
            "operator_responsibility": "operator_responsibility_report.json",
            "review_boards": "review_boards_report.json",
            "decision_matrix": "decision_matrix_report.json",
            "control_evidence": "control_evidence_report.json",
            "policy_registry": "policy_registry_report.json",
            "readiness_gates": "readiness_gates_report.json",
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
