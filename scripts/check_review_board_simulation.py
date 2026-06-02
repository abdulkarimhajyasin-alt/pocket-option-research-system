"""Validate review board simulation outputs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.review_board_simulation.schemas import (  # noqa: E402
    FORBIDDEN_DECISION_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.review_board_simulation.service import ReviewBoardSimulationService  # noqa: E402


def main() -> None:
    """Run review board simulation compliance checks."""
    run = ReviewBoardSimulationService(PROJECT_ROOT).run_full_review_board_simulation()
    module_dir = PROJECT_ROOT / "app" / "review_board_simulation"
    storage_dir = PROJECT_ROOT / "storage" / "review_board_simulation"
    report_dir = PROJECT_ROOT / "reports" / "review_board_simulation"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "source_loader.py",
        "board_registry.py",
        "review_simulator.py",
        "gate_dry_run.py",
        "evidence_review.py",
        "blocker_analysis.py",
        "decision_scoring.py",
        "findings.py",
        "readiness.py",
        "diagnostics.py",
        "recommendations.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "source_inventory.json",
        "board_registry.json",
        "board_simulation_results.json",
        "gate_dry_run_results.json",
        "evidence_review.json",
        "blocker_analysis.json",
        "decision_scores.json",
        "findings.json",
        "readiness_summary.json",
        "diagnostics.json",
        "recommendations.json",
        "summary.json",
    }
    required_reports = {
        "review_board_simulation_summary.json",
        "source_inventory_report.json",
        "board_registry_report.json",
        "board_simulation_report.json",
        "gate_dry_run_report.json",
        "evidence_review_report.json",
        "blocker_analysis_report.json",
        "decision_scores_report.json",
        "findings_report.json",
        "readiness_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    routes = [
        "/review-board-simulation",
        "/api/review-board-simulation",
        "/api/review-board-simulation/boards",
        "/api/review-board-simulation/decisions",
        "/api/review-board-simulation/gates",
        "/api/review-board-simulation/evidence",
        "/api/review-board-simulation/blockers",
        "/api/review-board-simulation/scores",
        "/api/review-board-simulation/findings",
        "/api/review-board-simulation/readiness",
        "/api/review-board-simulation/diagnostics",
        "/api/review-board-simulation/recommendations",
    ]
    responses = {route: client.get(route) for route in routes}
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()
    payload_text = json.dumps(run.payloads, ensure_ascii=False)
    checks = {
        "module_exists": module_dir.exists(),
        "required_modules": required_modules.issubset(
            {path.name for path in module_dir.glob("*.py")}
        ),
        "scripts": all(
            (PROJECT_ROOT / "scripts" / name).exists()
            for name in (
                "run_review_board_simulation.py",
                "check_review_board_simulation.py",
            )
        ),
        "tests": (PROJECT_ROOT / "tests" / "test_review_board_simulation.py").exists(),
        "dashboard_template": (
            PROJECT_ROOT
            / "app"
            / "templates"
            / "dashboard"
            / "review_board_simulation.html"
        ).exists(),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "storage": required_storage.issubset(
            {path.name for path in storage_dir.glob("*.json")}
        ),
        "json_valid": all(
            _valid_json(path)
            for path in list(report_dir.glob("*.json")) + list(storage_dir.glob("*.json"))
        ),
        "simulation_only": run.summary.get("simulation_only") is True,
        "review_only": run.summary.get("review_only") is True,
        "dry_run_only": run.summary.get("dry_run_only") is True,
        "governance_only": run.summary.get("governance_only") is True,
        "design_only": run.summary.get("design_only") is True,
        "architecture_only": run.summary.get("architecture_only") is True,
        "research_local_only": run.summary.get("research_only")
        and run.summary.get("local_only"),
        "no_forbidden_source": not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS),
        "routes": all(response.status_code == 200 for response in responses.values()),
        "arabic": "محاكاة مجالس المراجعة" in responses["/review-board-simulation"].text,
        "forbidden_states_absent": not any(
            state in payload_text for state in FORBIDDEN_DECISION_STATES
        ),
        "no_forbidden_capabilities": all(
            run.summary.get(key) is True
            for key in (
                "no_broker_access",
                "no_execution_capability",
                "no_authentication",
                "no_credentials",
                "no_browser_automation",
                "no_money_handling",
            )
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
