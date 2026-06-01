"""Validate Trading System Architecture Program foundation outputs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.trading_architecture_program.schemas import FORBIDDEN_SOURCE_TERMS  # noqa: E402
from app.trading_architecture_program.service import (  # noqa: E402
    TradingArchitectureProgramService,
)


def main() -> None:
    """Run architecture-program compliance checks."""
    run = TradingArchitectureProgramService(PROJECT_ROOT).run_full_program_foundation()
    module_dir = PROJECT_ROOT / "app" / "trading_architecture_program"
    storage_dir = PROJECT_ROOT / "storage" / "trading_architecture_program"
    report_dir = PROJECT_ROOT / "reports" / "trading_architecture_program"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "governance.py",
        "decision_gates.py",
        "workstreams.py",
        "program_registry.py",
        "architecture_domains.py",
        "diagnostics.py",
        "recommendations.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "program_registry.json",
        "domains.json",
        "gates.json",
        "workstreams.json",
        "diagnostics.json",
        "recommendations.json",
    }
    required_reports = {
        "program_summary.json",
        "domain_report.json",
        "gate_report.json",
        "workstream_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    responses = {
        "page": client.get("/trading-architecture-program"),
        "root": client.get("/api/trading-architecture-program"),
        "gates": client.get("/api/trading-architecture-program/gates"),
        "workstreams": client.get("/api/trading-architecture-program/workstreams"),
        "domains": client.get("/api/trading-architecture-program/domains"),
        "diagnostics": client.get("/api/trading-architecture-program/diagnostics"),
    }
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()
    checks = {
        "module_exists": module_dir.exists(),
        "required_modules": required_modules.issubset(
            {path.name for path in module_dir.glob("*.py")}
        ),
        "scripts": all(
            (PROJECT_ROOT / "scripts" / name).exists()
            for name in (
                "run_trading_architecture_program.py",
                "check_trading_architecture_program.py",
            )
        ),
        "tests": (PROJECT_ROOT / "tests" / "test_trading_architecture_program.py").exists(),
        "reports": required_reports.issubset({path.name for path in report_dir.glob("*.json")}),
        "storage": required_storage.issubset({path.name for path in storage_dir.glob("*.json")}),
        "json_valid": all(
            _valid_json(path)
            for path in list(report_dir.glob("*.json")) + list(storage_dir.glob("*.json"))
        ),
        "architecture_only": run.summary.get("architecture_only") is True,
        "no_execution": run.summary.get("no_execution_capability") is True,
        "no_broker": run.summary.get("no_broker_capability") is True,
        "no_trading": run.summary.get("no_trading_capability") is True,
        "no_forbidden_source": not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS),
        "routes": all(response.status_code == 200 for response in responses.values()),
        "arabic": "برنامج هندسة نظام التداول المستقبلي" in responses["page"].text,
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
