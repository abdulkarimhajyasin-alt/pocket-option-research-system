"""Diagnostics for operational governance outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.operational_governance.schemas import (
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)


class OperationalGovernanceDiagnostics:
    """Evaluate governance completeness and source safety."""

    def evaluate(self, project_root: Path, payloads: dict[str, Any]) -> list[dict[str, str]]:
        diagnostics: list[dict[str, str]] = []
        required = {
            "authority_model",
            "approval_workflows",
            "change_management",
            "release_governance",
            "incident_escalation",
            "kill_switch_governance",
            "audit_controls",
            "operator_responsibility",
            "review_boards",
            "decision_matrix",
            "control_evidence",
            "policy_registry",
            "readiness_gates",
        }
        for key in sorted(required.difference(payloads)):
            diagnostics.append({"code": f"missing-{key}", "severity": "مرتفع", "message": key})
        text = str(payloads)
        for state in FORBIDDEN_READINESS_STATES:
            if state in text:
                diagnostics.append(
                    {
                        "code": "forbidden-readiness-state",
                        "severity": "مرتفع",
                        "message": state,
                    }
                )
        diagnostics.extend(self._source_diagnostics(project_root))
        return diagnostics

    def _source_diagnostics(self, project_root: Path) -> list[dict[str, str]]:
        module_dir = project_root / "app" / "operational_governance"
        if not module_dir.exists():
            return [{"code": "missing-module", "severity": "مرتفع", "message": "module"}]
        text = "\n".join(
            path.read_text(encoding="utf-8").lower() for path in module_dir.glob("*.py")
        )
        return [
            {
                "code": "forbidden-implementation-artifact",
                "severity": "مرتفع",
                "message": term,
            }
            for term in FORBIDDEN_SOURCE_TERMS
            if term in text
        ]
