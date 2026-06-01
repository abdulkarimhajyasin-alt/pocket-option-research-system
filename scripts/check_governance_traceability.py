"""Validate governance traceability mapping outputs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.governance_traceability.schemas import (  # noqa: E402
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.governance_traceability.service import GovernanceTraceabilityService  # noqa: E402


def main() -> None:
    """Run traceability compliance checks."""
    run = GovernanceTraceabilityService(PROJECT_ROOT).run_full_governance_traceability()
    module_dir = PROJECT_ROOT / "app" / "governance_traceability"
    storage_dir = PROJECT_ROOT / "storage" / "governance_traceability"
    report_dir = PROJECT_ROOT / "reports" / "governance_traceability"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "source_loader.py",
        "mapping_engine.py",
        "control_matrix.py",
        "evidence_matrix.py",
        "readiness_mapping.py",
        "risk_mapping.py",
        "incident_mapping.py",
        "release_mapping.py",
        "monitoring_mapping.py",
        "policy_mapping.py",
        "coverage.py",
        "diagnostics.py",
        "recommendations.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "source_inventory.json",
        "control_mappings.json",
        "control_matrix.json",
        "evidence_matrix.json",
        "readiness_mapping.json",
        "risk_mapping.json",
        "incident_mapping.json",
        "release_mapping.json",
        "monitoring_mapping.json",
        "policy_mapping.json",
        "coverage_summary.json",
        "diagnostics.json",
        "recommendations.json",
        "summary.json",
    }
    required_reports = {
        "governance_traceability_summary.json",
        "source_inventory_report.json",
        "control_mappings_report.json",
        "control_matrix_report.json",
        "evidence_matrix_report.json",
        "readiness_mapping_report.json",
        "risk_mapping_report.json",
        "incident_mapping_report.json",
        "release_mapping_report.json",
        "monitoring_mapping_report.json",
        "policy_mapping_report.json",
        "coverage_summary_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    routes = [
        "/governance-traceability",
        "/api/governance-traceability",
        "/api/governance-traceability/mappings",
        "/api/governance-traceability/control-matrix",
        "/api/governance-traceability/evidence-matrix",
        "/api/governance-traceability/readiness",
        "/api/governance-traceability/risks",
        "/api/governance-traceability/incidents",
        "/api/governance-traceability/releases",
        "/api/governance-traceability/monitoring",
        "/api/governance-traceability/policies",
        "/api/governance-traceability/coverage",
        "/api/governance-traceability/diagnostics",
        "/api/governance-traceability/recommendations",
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
                "run_governance_traceability.py",
                "check_governance_traceability.py",
            )
        ),
        "tests": (PROJECT_ROOT / "tests" / "test_governance_traceability.py").exists(),
        "dashboard_template": (
            PROJECT_ROOT / "app" / "templates" / "dashboard" / "governance_traceability.html"
        ).exists(),
        "reports": required_reports.issubset({path.name for path in report_dir.glob("*.json")}),
        "storage": required_storage.issubset({path.name for path in storage_dir.glob("*.json")}),
        "json_valid": all(
            _valid_json(path)
            for path in list(report_dir.glob("*.json")) + list(storage_dir.glob("*.json"))
        ),
        "traceability_only": run.summary.get("traceability_only") is True,
        "governance_only": run.summary.get("governance_only") is True,
        "design_only": run.summary.get("design_only") is True,
        "architecture_only": run.summary.get("architecture_only") is True,
        "research_local_only": run.summary.get("research_only") and run.summary.get("local_only"),
        "no_forbidden_source": not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS),
        "routes": all(response.status_code == 200 for response in responses.values()),
        "arabic": "تتبع الحوكمة وربط الضوابط" in responses["/governance-traceability"].text,
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
