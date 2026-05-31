"""Diagnostics for the manual snapshot import workflow."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.snapshot_import.service import SnapshotImportService  # noqa: E402


def main() -> None:
    """Run snapshot import compliance checks."""
    run = SnapshotImportService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/snapshot-import")
    api_response = client.get("/api/snapshot-import")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/snapshot_import.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "import_summary.json",
        "validation_report.json",
        "processing_report.json",
        "quality_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "snapshot_import"
    metadata = run.result.metadata
    checks = {
        "workflow_score": 0 <= run.result.workflow.score <= 100,
        "validation_score": 0 <= run.result.validation.score <= 100,
        "processing_score": 0 <= run.result.processing.score <= 100,
        "quality_score": 0 <= run.result.quality.score <= 100,
        "safety": run.result.safety.status == "PASS",
        "imports": len(run.result.imports) >= 1,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "مركز استيراد اللقطات",
                "رفع ملف يدوي",
                "توزيع اللقطات",
                "توزيع السلامة",
            )
        )
        and "Snapshot Import" not in template_text,
        "manual_only": metadata.get("manual_only") is True,
        "observation_only": metadata.get("observation_only") is True,
        "not_execution": metadata.get("not_execution") is True,
        "not_order_placement": metadata.get("not_order_placement") is True,
        "not_account_login": metadata.get("not_account_login") is True,
        "not_broker_authentication": metadata.get("not_broker_authentication") is True,
        "not_credential_handling": metadata.get("not_credential_handling") is True,
        "not_browser_automation": metadata.get("not_browser_automation") is True,
        "not_broker_control": metadata.get("not_broker_control") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
