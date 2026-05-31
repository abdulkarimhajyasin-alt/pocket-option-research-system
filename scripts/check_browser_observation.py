"""Diagnostics for the read-only browser observation adapter."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.browser_observation.service import BrowserObservationService  # noqa: E402
from app.dashboard.routes import create_dashboard_app  # noqa: E402


def main() -> None:
    """Run browser observation compliance checks."""
    run = BrowserObservationService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/browser-observation")
    api_response = client.get("/api/browser-observation")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/browser_observation.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "observation_summary.json",
        "artifact_report.json",
        "validation_report.json",
        "visibility_report.json",
        "monitoring_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "browser_observation"
    metadata = run.result.metadata
    checks = {
        "adapter_score": 0 <= run.result.adapter.score <= 100,
        "parse_score": 0 <= run.result.parse.score <= 100,
        "validation_score": 0 <= run.result.validation.score <= 100,
        "visibility_score": 0 <= run.result.visibility.score <= 100,
        "monitoring_score": 0 <= run.result.monitoring.score <= 100,
        "safety": run.result.safety.status == "PASS",
        "artifacts": len(run.result.artifacts) >= 5,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "مراقبة المتصفح للقراءة فقط",
                "درجة الجاهزية",
                "توزيع اللقطات",
                "توزيع السلامة",
            )
        )
        and "Browser Observation" not in template_text,
        "read_only": metadata.get("read_only") is True,
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
