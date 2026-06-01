"""Validate control assurance outputs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.control_assurance.schemas import (  # noqa: E402
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.control_assurance.service import ControlAssuranceService  # noqa: E402
from app.dashboard.routes import create_dashboard_app  # noqa: E402


def main() -> None:
    """Run assurance compliance checks."""
    run = ControlAssuranceService(PROJECT_ROOT).run_full_control_assurance()
    module_dir = PROJECT_ROOT / "app" / "control_assurance"
    storage_dir = PROJECT_ROOT / "storage" / "control_assurance"
    report_dir = PROJECT_ROOT / "reports" / "control_assurance"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "source_loader.py",
        "assurance_engine.py",
        "review_readiness.py",
        "evidence_assessment.py",
        "owner_assessment.py",
        "policy_assessment.py",
        "gate_assessment.py",
        "weakness_assessment.py",
        "audit_readiness.py",
        "scoring.py",
        "diagnostics.py",
        "recommendations.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "source_inventory.json",
        "control_quality.json",
        "evidence_sufficiency.json",
        "owner_clarity.json",
        "policy_completeness.json",
        "gate_maturity.json",
        "weakness_assessment.json",
        "audit_readiness.json",
        "review_readiness.json",
        "scorecard.json",
        "diagnostics.json",
        "recommendations.json",
        "summary.json",
    }
    required_reports = {
        "control_assurance_summary.json",
        "source_inventory_report.json",
        "control_quality_report.json",
        "evidence_sufficiency_report.json",
        "owner_clarity_report.json",
        "policy_completeness_report.json",
        "gate_maturity_report.json",
        "weakness_assessment_report.json",
        "audit_readiness_report.json",
        "review_readiness_report.json",
        "scorecard_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    routes = [
        "/control-assurance",
        "/api/control-assurance",
        "/api/control-assurance/control-quality",
        "/api/control-assurance/evidence",
        "/api/control-assurance/owners",
        "/api/control-assurance/policies",
        "/api/control-assurance/gates",
        "/api/control-assurance/weaknesses",
        "/api/control-assurance/audit-readiness",
        "/api/control-assurance/review-readiness",
        "/api/control-assurance/scorecard",
        "/api/control-assurance/diagnostics",
        "/api/control-assurance/recommendations",
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
            for name in ("run_control_assurance.py", "check_control_assurance.py")
        ),
        "tests": (PROJECT_ROOT / "tests" / "test_control_assurance.py").exists(),
        "dashboard_template": (
            PROJECT_ROOT / "app" / "templates" / "dashboard" / "control_assurance.html"
        ).exists(),
        "reports": required_reports.issubset({path.name for path in report_dir.glob("*.json")}),
        "storage": required_storage.issubset({path.name for path in storage_dir.glob("*.json")}),
        "json_valid": all(
            _valid_json(path)
            for path in list(report_dir.glob("*.json")) + list(storage_dir.glob("*.json"))
        ),
        "assurance_only": run.summary.get("assurance_only") is True,
        "review_readiness_only": run.summary.get("review_readiness_only") is True,
        "governance_only": run.summary.get("governance_only") is True,
        "design_only": run.summary.get("design_only") is True,
        "architecture_only": run.summary.get("architecture_only") is True,
        "research_local_only": run.summary.get("research_only") and run.summary.get("local_only"),
        "no_forbidden_source": not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS),
        "routes": all(response.status_code == 200 for response in responses.values()),
        "arabic": "تأكيد الضوابط وجاهزية المراجعة" in responses["/control-assurance"].text,
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
