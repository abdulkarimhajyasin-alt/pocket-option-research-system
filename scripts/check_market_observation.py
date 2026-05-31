"""Diagnostics for the canonical market observation pipeline."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.market_observation.service import MarketObservationService  # noqa: E402


def main() -> None:
    """Run market observation compliance checks."""
    run = MarketObservationService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/market-observation")
    api_response = client.get("/api/market-observation")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/market_observation.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "observation_summary.json",
        "source_report.json",
        "quality_report.json",
        "confidence_report.json",
        "coverage_report.json",
        "validation_report.json",
        "diagnostics_report.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "market_observation"
    metadata = run.result.metadata
    checks = {
        "observations": len(run.result.observations) >= 5,
        "validation": 0 <= run.result.validation.score <= 100,
        "aggregate": 0 <= run.result.aggregate.score <= 100,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "مصدر مراقبة السوق الموحد",
                "التغطية",
                "توزيع المصادر",
                "جودة المصادر",
            )
        )
        and "Market Observation" not in template_text,
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
