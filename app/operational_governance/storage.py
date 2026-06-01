"""Storage writer for operational governance outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class OperationalGovernanceStorage:
    """Write governance artifacts to local storage."""

    def __init__(self, output_dir: Path | str = "storage/operational_governance") -> None:
        self.output_dir = Path(output_dir)

    def save(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "authority_model": "authority_model.json",
            "approval_workflows": "approval_workflows.json",
            "change_management": "change_management.json",
            "release_governance": "release_governance.json",
            "incident_escalation": "incident_escalation.json",
            "kill_switch_governance": "kill_switch_governance.json",
            "audit_controls": "audit_controls.json",
            "operator_responsibility": "operator_responsibility.json",
            "review_boards": "review_boards.json",
            "decision_matrix": "decision_matrix.json",
            "control_evidence": "control_evidence.json",
            "policy_registry": "policy_registry.json",
            "readiness_gates": "readiness_gates.json",
            "diagnostics": "diagnostics.json",
            "recommendations": "recommendations.json",
            "summary": "summary.json",
        }
        return self._write_mapping(payloads, mapping)

    def _write_mapping(self, payloads: dict[str, Any], mapping: dict[str, str]) -> dict[str, str]:
        paths = {}
        for key, filename in mapping.items():
            path = self.output_dir / filename
            path.write_text(
                json.dumps(payloads.get(key, {}), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            paths[key] = str(path)
        return paths
