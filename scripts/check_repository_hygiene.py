"""Validate repository hygiene outputs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.repository_hygiene.schemas import FORBIDDEN_SOURCE_TERMS  # noqa: E402
from app.repository_hygiene.service import RepositoryHygieneService  # noqa: E402


def main() -> None:
    """Run repository hygiene compliance checks."""
    run = RepositoryHygieneService(PROJECT_ROOT).run_full_repository_hygiene()
    module_dir = PROJECT_ROOT / "app" / "repository_hygiene"
    storage_dir = PROJECT_ROOT / "storage" / "repository_hygiene"
    report_dir = PROJECT_ROOT / "reports" / "repository_hygiene"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "git_status_parser.py",
        "artifact_inventory.py",
        "retention_policy.py",
        "cleanup_planner.py",
        "ignore_recommendations.py",
        "duplicate_detection.py",
        "stale_detection.py",
        "archive_policy.py",
        "report_policy.py",
        "storage_policy.py",
        "hygiene_scoring.py",
        "diagnostics.py",
        "recommendations.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "git_status_inventory.json",
        "artifact_inventory.json",
        "artifact_classification.json",
        "retention_policy.json",
        "cleanup_plan.json",
        "ignore_recommendations.json",
        "duplicate_artifacts.json",
        "stale_artifacts.json",
        "archive_policy.json",
        "scorecard.json",
        "diagnostics.json",
        "recommendations.json",
        "summary.json",
    }
    required_reports = {
        "repository_hygiene_summary.json",
        "git_status_inventory_report.json",
        "artifact_inventory_report.json",
        "artifact_classification_report.json",
        "retention_policy_report.json",
        "cleanup_plan_report.json",
        "ignore_recommendations_report.json",
        "duplicate_artifacts_report.json",
        "stale_artifacts_report.json",
        "archive_policy_report.json",
        "scorecard_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    routes = [
        "/repository-hygiene",
        "/api/repository-hygiene",
        "/api/repository-hygiene/git-status",
        "/api/repository-hygiene/artifacts",
        "/api/repository-hygiene/retention-policy",
        "/api/repository-hygiene/cleanup-plan",
        "/api/repository-hygiene/ignore-recommendations",
        "/api/repository-hygiene/duplicates",
        "/api/repository-hygiene/stale",
        "/api/repository-hygiene/archive-policy",
        "/api/repository-hygiene/scorecard",
        "/api/repository-hygiene/diagnostics",
        "/api/repository-hygiene/recommendations",
    ]
    responses = {route: client.get(route) for route in routes}
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()
    cleanup_text = json.dumps(run.payloads["cleanup_plan"], ensure_ascii=False)
    checks = {
        "module_exists": module_dir.exists(),
        "required_modules": required_modules.issubset(
            {path.name for path in module_dir.glob("*.py")}
        ),
        "scripts": all(
            (PROJECT_ROOT / "scripts" / name).exists()
            for name in ("run_repository_hygiene.py", "check_repository_hygiene.py")
        ),
        "tests": (PROJECT_ROOT / "tests" / "test_repository_hygiene.py").exists(),
        "dashboard_template": (
            PROJECT_ROOT / "app" / "templates" / "dashboard" / "repository_hygiene.html"
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
        "repository_hygiene_only": run.summary.get("repository_hygiene_only") is True,
        "artifact_policy_only": run.summary.get("artifact_policy_only") is True,
        "non_destructive": run.summary.get("non_destructive") is True,
        "no_destructive_cleanup": "destructive_action_forbidden" in cleanup_text,
        "no_forbidden_source": not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS),
        "routes": all(response.status_code == 200 for response in responses.values()),
        "arabic": "نظافة المستودع" in responses["/repository-hygiene"].text,
        "safety_boundary": all(
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
