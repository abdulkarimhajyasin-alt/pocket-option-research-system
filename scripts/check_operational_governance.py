"""Validate operational governance framework outputs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.operational_governance.schemas import (  # noqa: E402
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.operational_governance.service import OperationalGovernanceService  # noqa: E402


def main() -> None:
    """Run governance compliance checks."""
    run = OperationalGovernanceService(PROJECT_ROOT).run_full_operational_governance()
    module_dir = PROJECT_ROOT / "app" / "operational_governance"
    storage_dir = PROJECT_ROOT / "storage" / "operational_governance"
    report_dir = PROJECT_ROOT / "reports" / "operational_governance"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "authority_model.py",
        "approval_workflows.py",
        "change_management.py",
        "release_governance.py",
        "incident_escalation.py",
        "kill_switch_governance.py",
        "audit_controls.py",
        "operator_responsibility.py",
        "review_boards.py",
        "decision_matrix.py",
        "control_evidence.py",
        "policy_registry.py",
        "readiness_gates.py",
        "diagnostics.py",
        "recommendations.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "authority_model.json",
        "approval_workflows.json",
        "change_management.json",
        "release_governance.json",
        "incident_escalation.json",
        "kill_switch_governance.json",
        "audit_controls.json",
        "operator_responsibility.json",
        "review_boards.json",
        "decision_matrix.json",
        "control_evidence.json",
        "policy_registry.json",
        "readiness_gates.json",
        "diagnostics.json",
        "recommendations.json",
        "summary.json",
    }
    required_reports = {
        "operational_governance_summary.json",
        "authority_model_report.json",
        "approval_workflows_report.json",
        "change_management_report.json",
        "release_governance_report.json",
        "incident_escalation_report.json",
        "kill_switch_governance_report.json",
        "audit_controls_report.json",
        "operator_responsibility_report.json",
        "review_boards_report.json",
        "decision_matrix_report.json",
        "control_evidence_report.json",
        "policy_registry_report.json",
        "readiness_gates_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    routes = [
        "/operational-governance",
        "/api/operational-governance",
        "/api/operational-governance/authority",
        "/api/operational-governance/approval-workflows",
        "/api/operational-governance/change-management",
        "/api/operational-governance/release-governance",
        "/api/operational-governance/incidents",
        "/api/operational-governance/kill-switch",
        "/api/operational-governance/audit-controls",
        "/api/operational-governance/operators",
        "/api/operational-governance/review-boards",
        "/api/operational-governance/decision-matrix",
        "/api/operational-governance/control-evidence",
        "/api/operational-governance/policies",
        "/api/operational-governance/readiness-gates",
        "/api/operational-governance/diagnostics",
        "/api/operational-governance/recommendations",
    ]
    responses = {route: client.get(route) for route in routes}
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()
    payload_text = json.dumps(run.summary, ensure_ascii=False)
    checks = {
        "module_exists": module_dir.exists(),
        "required_modules": required_modules.issubset(
            {path.name for path in module_dir.glob("*.py")}
        ),
        "scripts": all(
            (PROJECT_ROOT / "scripts" / name).exists()
            for name in (
                "run_operational_governance.py",
                "check_operational_governance.py",
            )
        ),
        "tests": (PROJECT_ROOT / "tests" / "test_operational_governance.py").exists(),
        "dashboard_template": (
            PROJECT_ROOT / "app" / "templates" / "dashboard" / "operational_governance.html"
        ).exists(),
        "reports": required_reports.issubset({path.name for path in report_dir.glob("*.json")}),
        "storage": required_storage.issubset({path.name for path in storage_dir.glob("*.json")}),
        "json_valid": all(
            _valid_json(path)
            for path in list(report_dir.glob("*.json")) + list(storage_dir.glob("*.json"))
        ),
        "governance_only": run.summary.get("governance_only") is True,
        "design_only": run.summary.get("design_only") is True,
        "architecture_only": run.summary.get("architecture_only") is True,
        "research_local_only": run.summary.get("research_only") and run.summary.get("local_only"),
        "no_forbidden_source": not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS),
        "routes": all(response.status_code == 200 for response in responses.values()),
        "arabic": "إطار الحوكمة والتحكم التشغيلي" in responses["/operational-governance"].text,
        "forbidden_states_absent": not any(
            state in payload_text for state in FORBIDDEN_READINESS_STATES
        ),
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


def _valid_json(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return True


if __name__ == "__main__":
    main()
