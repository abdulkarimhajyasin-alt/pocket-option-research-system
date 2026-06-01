"""Validate trading requirements specification outputs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.trading_requirements.schemas import (  # noqa: E402
    FORBIDDEN_DECISION_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.trading_requirements.service import TradingRequirementsService  # noqa: E402


def main() -> None:
    """Run requirements compliance checks."""
    run = TradingRequirementsService(PROJECT_ROOT).run_full_requirements_specification()
    module_dir = PROJECT_ROOT / "app" / "trading_requirements"
    storage_dir = PROJECT_ROOT / "storage" / "trading_requirements"
    report_dir = PROJECT_ROOT / "reports" / "trading_requirements"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "functional.py",
        "non_functional.py",
        "safety_requirements.py",
        "risk_requirements.py",
        "compliance_constraints.py",
        "operational_constraints.py",
        "broker_constraints.py",
        "execution_constraints.py",
        "monitoring_constraints.py",
        "data_constraints.py",
        "go_no_go.py",
        "diagnostics.py",
        "recommendations.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "functional_requirements.json",
        "non_functional_requirements.json",
        "safety_requirements.json",
        "risk_requirements.json",
        "compliance_constraints.json",
        "operational_constraints.json",
        "broker_constraints.json",
        "execution_constraints.json",
        "monitoring_constraints.json",
        "data_constraints.json",
        "go_no_go_criteria.json",
        "coverage_summary.json",
        "diagnostics.json",
        "recommendations.json",
        "summary.json",
    }
    required_reports = {
        "requirements_summary.json",
        "functional_requirements_report.json",
        "non_functional_requirements_report.json",
        "safety_requirements_report.json",
        "risk_requirements_report.json",
        "compliance_constraints_report.json",
        "operational_constraints_report.json",
        "broker_constraints_report.json",
        "execution_constraints_report.json",
        "monitoring_constraints_report.json",
        "data_constraints_report.json",
        "go_no_go_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    routes = [
        "/trading-requirements",
        "/api/trading-requirements",
        "/api/trading-requirements/functional",
        "/api/trading-requirements/non-functional",
        "/api/trading-requirements/safety",
        "/api/trading-requirements/risk",
        "/api/trading-requirements/compliance",
        "/api/trading-requirements/broker",
        "/api/trading-requirements/execution",
        "/api/trading-requirements/monitoring",
        "/api/trading-requirements/data",
        "/api/trading-requirements/go-no-go",
        "/api/trading-requirements/diagnostics",
        "/api/trading-requirements/recommendations",
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
            for name in ("run_trading_requirements.py", "check_trading_requirements.py")
        ),
        "tests": (PROJECT_ROOT / "tests" / "test_trading_requirements.py").exists(),
        "dashboard_template": (
            PROJECT_ROOT / "app" / "templates" / "dashboard" / "trading_requirements.html"
        ).exists(),
        "reports": required_reports.issubset({path.name for path in report_dir.glob("*.json")}),
        "storage": required_storage.issubset({path.name for path in storage_dir.glob("*.json")}),
        "json_valid": all(
            _valid_json(path)
            for path in list(report_dir.glob("*.json")) + list(storage_dir.glob("*.json"))
        ),
        "requirements_only": run.summary.get("requirements_only") is True,
        "architecture_only": run.summary.get("architecture_only") is True,
        "research_local_only": run.summary.get("research_only") and run.summary.get("local_only"),
        "no_forbidden_source": not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS),
        "routes": all(response.status_code == 200 for response in responses.values()),
        "arabic": "مواصفات متطلبات نظام التداول المستقبلي"
        in responses["/trading-requirements"].text,
        "forbidden_states_absent": not any(
            state in payload_text for state in FORBIDDEN_DECISION_STATES
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
