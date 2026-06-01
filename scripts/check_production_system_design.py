"""Validate production system design blueprint outputs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.production_system_design.schemas import (  # noqa: E402
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.production_system_design.service import ProductionSystemDesignService  # noqa: E402


def main() -> None:
    """Run production design compliance checks."""
    run = ProductionSystemDesignService(PROJECT_ROOT).run_full_production_design()
    module_dir = PROJECT_ROOT / "app" / "production_system_design"
    storage_dir = PROJECT_ROOT / "storage" / "production_system_design"
    report_dir = PROJECT_ROOT / "reports" / "production_system_design"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "topology.py",
        "service_boundaries.py",
        "runtime_architecture.py",
        "environment_strategy.py",
        "configuration_strategy.py",
        "secrets_strategy.py",
        "database_strategy.py",
        "event_queue_strategy.py",
        "logging_strategy.py",
        "monitoring_strategy.py",
        "alerting_strategy.py",
        "incident_response.py",
        "backup_recovery.py",
        "release_rollback.py",
        "readiness_gates.py",
        "diagnostics.py",
        "recommendations.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "topology.json",
        "service_boundaries.json",
        "runtime_architecture.json",
        "environment_strategy.json",
        "configuration_strategy.json",
        "secrets_strategy.json",
        "database_strategy.json",
        "event_queue_strategy.json",
        "logging_strategy.json",
        "monitoring_strategy.json",
        "alerting_strategy.json",
        "incident_response.json",
        "backup_recovery.json",
        "release_rollback.json",
        "readiness_gates.json",
        "diagnostics.json",
        "recommendations.json",
        "summary.json",
    }
    required_reports = {
        "production_design_summary.json",
        "topology_report.json",
        "service_boundaries_report.json",
        "runtime_architecture_report.json",
        "environment_strategy_report.json",
        "configuration_strategy_report.json",
        "secrets_strategy_report.json",
        "database_strategy_report.json",
        "event_queue_strategy_report.json",
        "logging_strategy_report.json",
        "monitoring_strategy_report.json",
        "alerting_strategy_report.json",
        "incident_response_report.json",
        "backup_recovery_report.json",
        "release_rollback_report.json",
        "readiness_gates_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    routes = [
        "/production-system-design",
        "/api/production-system-design",
        "/api/production-system-design/topology",
        "/api/production-system-design/service-boundaries",
        "/api/production-system-design/runtime",
        "/api/production-system-design/environments",
        "/api/production-system-design/configuration",
        "/api/production-system-design/secrets",
        "/api/production-system-design/database",
        "/api/production-system-design/events",
        "/api/production-system-design/logging",
        "/api/production-system-design/monitoring",
        "/api/production-system-design/alerting",
        "/api/production-system-design/incidents",
        "/api/production-system-design/backup-recovery",
        "/api/production-system-design/release-rollback",
        "/api/production-system-design/readiness-gates",
        "/api/production-system-design/diagnostics",
        "/api/production-system-design/recommendations",
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
            for name in ("run_production_system_design.py", "check_production_system_design.py")
        ),
        "tests": (PROJECT_ROOT / "tests" / "test_production_system_design.py").exists(),
        "dashboard_template": (
            PROJECT_ROOT / "app" / "templates" / "dashboard" / "production_system_design.html"
        ).exists(),
        "reports": required_reports.issubset({path.name for path in report_dir.glob("*.json")}),
        "storage": required_storage.issubset({path.name for path in storage_dir.glob("*.json")}),
        "json_valid": all(
            _valid_json(path)
            for path in list(report_dir.glob("*.json")) + list(storage_dir.glob("*.json"))
        ),
        "design_only": run.summary.get("design_only") is True,
        "architecture_only": run.summary.get("architecture_only") is True,
        "research_local_only": run.summary.get("research_only") and run.summary.get("local_only"),
        "no_forbidden_source": not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS),
        "routes": all(response.status_code == 200 for response in responses.values()),
        "arabic": "مخطط تصميم النظام الإنتاجي المستقبلي"
        in responses["/production-system-design"].text,
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
