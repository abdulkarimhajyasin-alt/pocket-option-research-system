"""Diagnostics for the passive external observation sandbox."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.external_observation.service import ExternalObservationService  # noqa: E402


def main() -> None:
    """Run external observation compliance checks."""
    run = ExternalObservationService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/external-observation")
    api_response = client.get("/api/external-observation")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/external_observation.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "sandbox_summary.json",
        "source_report.json",
        "validation_report.json",
        "monitoring_report.json",
        "health_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "external_observation"
    metadata = run.result.metadata
    checks = {
        "sandbox_score": 0 <= run.result.sandbox.score <= 100,
        "health_score": 0 <= run.result.health.score <= 100,
        "validation_score": 0 <= run.result.validation.score <= 100,
        "monitoring_score": 0 <= run.result.monitoring.score <= 100,
        "isolation": run.result.isolation.status == "PASS",
        "sources": len(run.result.sources) >= 4,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "بيئة المراقبة الخارجية",
                "درجة الجاهزية",
                "توزيع المصادر",
                "توزيع العزل",
            )
        )
        and "External Observation" not in template_text,
        "observation_only": metadata.get("observation_only") is True,
        "not_execution": metadata.get("not_execution") is True,
        "not_order_placement": metadata.get("not_order_placement") is True,
        "not_account_login": metadata.get("not_account_login") is True,
        "not_broker_authentication": metadata.get("not_broker_authentication") is True,
        "not_browser_automation": metadata.get("not_browser_automation") is True,
        "not_broker_control": metadata.get("not_broker_control") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
