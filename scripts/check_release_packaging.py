"""Validate final release packaging outputs and safety boundaries."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.release_packaging.schemas import (  # noqa: E402
    FORBIDDEN_RELEASE_STATUSES,
    RELEASE_ID,
    SAFE_RELEASE_STATUSES,
)
from app.release_packaging.service import ReleasePackagingService  # noqa: E402


def main() -> None:
    """Run release packaging compliance checks."""
    run = ReleasePackagingService(PROJECT_ROOT).run_full_release_packaging()
    module_dir = PROJECT_ROOT / "app" / "release_packaging"
    report_dir = PROJECT_ROOT / "reports" / "release_packaging"
    storage_dir = PROJECT_ROOT / "storage" / "release_packaging"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "repository_audit.py",
        "release_manifest.py",
        "release_notes.py",
        "project_status.py",
        "diagnostics.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "release_manifest.json",
        "project_status.json",
        "repository_audit.json",
        "diagnostics.json",
        "recommendations.json",
        "release_state.json",
    }
    required_reports = {
        "release_summary.json",
        "release_notes.json",
        "project_status_report.json",
        "architecture_summary.json",
        "repository_audit_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
        "release_manifest_report.json",
    }
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    responses = {
        "page": client.get("/release-packaging"),
        "root": client.get("/api/release-packaging"),
        "manifest": client.get("/api/release-packaging/manifest"),
        "status": client.get("/api/release-packaging/status"),
        "notes": client.get("/api/release-packaging/notes"),
        "diagnostics": client.get("/api/release-packaging/diagnostics"),
        "recommendations": client.get("/api/release-packaging/recommendations"),
    }
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()
    forbidden_terms = (
        "import selenium",
        "from selenium",
        "sync_playwright",
        "async_playwright",
        "webdriver",
        "place_order(",
        "api_key=",
        "secret_key=",
        "password=",
    )
    manifest_text = json.dumps(run.manifest, ensure_ascii=False)
    checks = {
        "module_exists": module_dir.exists(),
        "required_module_files": required_modules.issubset(
            {path.name for path in module_dir.glob("*.py")}
        ),
        "required_scripts": all(
            (PROJECT_ROOT / "scripts" / name).exists()
            for name in ("run_release_packaging.py", "check_release_packaging.py")
        ),
        "required_tests": (PROJECT_ROOT / "tests" / "test_release_packaging.py").exists(),
        "dashboard_template": (
            PROJECT_ROOT / "app" / "templates" / "dashboard" / "release_packaging.html"
        ).exists(),
        "reports": required_reports.issubset({path.name for path in report_dir.glob("*.json")}),
        "storage": required_storage.issubset({path.name for path in storage_dir.glob("*.json")}),
        "json_valid": all(
            _valid_json(path)
            for path in list(report_dir.glob("*.json")) + list(storage_dir.glob("*.json"))
        ),
        "release_id": run.manifest.get("release_id") == RELEASE_ID,
        "safe_release_status": run.manifest.get("release_status") in SAFE_RELEASE_STATUSES,
        "forbidden_states_absent": not any(
            state in manifest_text for state in FORBIDDEN_RELEASE_STATUSES
        ),
        "safety_boundary": all(run.manifest.get("safety_boundary", {}).values()),
        "dashboard_route": responses["page"].status_code == 200,
        "api_routes": all(response.status_code == 200 for response in responses.values()),
        "arabic_labels": "تغليف الإصدار النهائي" in responses["page"].text,
        "no_forbidden_capability": not any(term in module_text for term in forbidden_terms),
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
