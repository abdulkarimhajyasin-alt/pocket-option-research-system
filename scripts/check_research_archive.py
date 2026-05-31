"""Validate the research archive and versioning layer."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.research_archive.service import ResearchArchiveService  # noqa: E402


def main() -> None:
    """Run archive compliance checks."""
    service = ResearchArchiveService(PROJECT_ROOT)
    run = service.run_full_archive_cycle()
    storage_dir = PROJECT_ROOT / "storage" / "research_archive"
    report_dir = PROJECT_ROOT / "reports" / "research_archive"
    required_storage = {
        storage_dir / "archive_index.json",
        storage_dir / "versions.json",
        storage_dir / "latest_snapshot.json",
        storage_dir / "diffs" / "latest_diff.json",
        storage_dir / "evolution" / "evolution_report.json",
    }
    required_reports = {
        report_dir / "archive_summary.json",
        report_dir / "version_history.json",
        report_dir / "latest_version_report.json",
        report_dir / "diff_report.json",
        report_dir / "evolution_report.json",
        report_dir / "diagnostics_report.json",
        report_dir / "recommendations_report.json",
    }
    latest_dir = storage_dir / "snapshots" / run.version.version_label
    package_files = {
        latest_dir / "snapshot.json",
        latest_dir / "source_manifest.json",
        latest_dir / "safety_manifest.json",
        latest_dir / "diagnostics.json",
    }
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    routes = {
        "page": client.get("/research-archive"),
        "root": client.get("/api/research-archive"),
        "latest": client.get("/api/research-archive/latest"),
        "history": client.get("/api/research-archive/history"),
        "diff": client.get("/api/research-archive/diff"),
        "evolution": client.get("/api/research-archive/evolution"),
        "diagnostics": client.get("/api/research-archive/diagnostics"),
    }
    module_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PROJECT_ROOT / "app" / "research_archive").glob("*.py")
    ).lower()
    forbidden_markers = (
        "selenium",
        "playwright",
        "pocket option login",
        "webdriver",
        "api_key",
        "secret_key",
        "password",
        "place_order(",
        "buy(",
        "sell(",
    )
    checks = {
        "imports": run.snapshot.research_only is True,
        "storage_files": all(path.exists() for path in required_storage),
        "report_files": all(path.exists() for path in required_reports),
        "package_files": all(path.exists() for path in package_files),
        "latest_snapshot": (storage_dir / "latest_snapshot.json").exists(),
        "version_history": bool(service.get_version_history()),
        "research_only": run.snapshot.safety_status.get("research_only") is True,
        "local_only": run.snapshot.safety_status.get("local_only") is True,
        "no_forbidden_markers": not any(marker in module_text for marker in forbidden_markers),
        "dashboard_routes": all(response.status_code == 200 for response in routes.values()),
        "api_root_safe": routes["root"].json()["summary"]["research_only"] is True,
        "api_latest_safe": routes["latest"].json()["safety_boundary"]["research_only"] is True,
        "api_diagnostics_safe": routes["diagnostics"].json()["research_only"] is True,
        "arabic": "أرشيف البحث" in routes["page"].text,
        "json_valid": all(_valid_json(path) for path in required_storage | required_reports | package_files),
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
