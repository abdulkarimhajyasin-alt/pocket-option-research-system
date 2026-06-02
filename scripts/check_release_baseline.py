"""Validate release baseline reconciliation outputs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.release_baseline.schemas import (  # noqa: E402
    FORBIDDEN_BASELINE_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.release_baseline.service import ReleaseBaselineService  # noqa: E402


def main() -> None:
    """Run release baseline compliance checks."""
    run = ReleaseBaselineService(PROJECT_ROOT).run_full_release_baseline()
    module_dir = PROJECT_ROOT / "app" / "release_baseline"
    storage_dir = PROJECT_ROOT / "storage" / "release_baseline"
    report_dir = PROJECT_ROOT / "reports" / "release_baseline"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "source_loader.py",
        "baseline_inventory.py",
        "commit_classification.py",
        "artifact_reconciliation.py",
        "evidence_selection.py",
        "cleanup_checklist.py",
        "ignore_review.py",
        "prompt_file_policy.py",
        "validation_churn.py",
        "archive_reconciliation.py",
        "decision_matrix.py",
        "baseline_scoring.py",
        "diagnostics.py",
        "recommendations.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "source_inventory.json",
        "baseline_inventory.json",
        "commit_classification.json",
        "artifact_reconciliation.json",
        "evidence_selection.json",
        "cleanup_checklist.json",
        "ignore_review.json",
        "prompt_file_policy.json",
        "validation_churn.json",
        "archive_reconciliation.json",
        "decision_matrix.json",
        "scorecard.json",
        "diagnostics.json",
        "recommendations.json",
        "summary.json",
    }
    required_reports = {
        "release_baseline_summary.json",
        "source_inventory_report.json",
        "baseline_inventory_report.json",
        "commit_classification_report.json",
        "artifact_reconciliation_report.json",
        "evidence_selection_report.json",
        "cleanup_checklist_report.json",
        "ignore_review_report.json",
        "prompt_file_policy_report.json",
        "validation_churn_report.json",
        "archive_reconciliation_report.json",
        "decision_matrix_report.json",
        "scorecard_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    routes = [
        "/release-baseline",
        "/api/release-baseline",
        "/api/release-baseline/inventory",
        "/api/release-baseline/commit-classification",
        "/api/release-baseline/artifact-reconciliation",
        "/api/release-baseline/evidence",
        "/api/release-baseline/cleanup-checklist",
        "/api/release-baseline/ignore-review",
        "/api/release-baseline/prompt-policy",
        "/api/release-baseline/validation-churn",
        "/api/release-baseline/archive-reconciliation",
        "/api/release-baseline/decision-matrix",
        "/api/release-baseline/scorecard",
        "/api/release-baseline/diagnostics",
        "/api/release-baseline/recommendations",
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
            for name in ("run_release_baseline.py", "check_release_baseline.py")
        ),
        "tests": (PROJECT_ROOT / "tests" / "test_release_baseline.py").exists(),
        "dashboard_template": (
            PROJECT_ROOT / "app" / "templates" / "dashboard" / "release_baseline.html"
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
        "baseline_reconciliation_only": run.summary.get("baseline_reconciliation_only") is True,
        "manual_cleanup_planning_only": run.summary.get("manual_cleanup_planning_only") is True,
        "non_destructive": run.summary.get("non_destructive") is True,
        "no_destructive_cleanup": all(
            item.get("destructive_action_forbidden") is True
            for item in run.payloads["cleanup_checklist"].get("items", [])
        ),
        "no_forbidden_source": not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS),
        "routes": all(response.status_code == 200 for response in responses.values()),
        "arabic": "خط أساس الإصدار" in responses["/release-baseline"].text,
        "forbidden_states_absent": not any(
            state in payload_text for state in FORBIDDEN_BASELINE_STATES
        ),
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
