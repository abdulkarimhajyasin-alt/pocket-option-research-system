"""Diagnostics for passive broker observation readiness."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.broker_readiness.service import BrokerReadinessService  # noqa: E402
from app.dashboard.routes import create_dashboard_app  # noqa: E402


def main() -> None:
    """Run broker readiness compliance checks."""
    run = BrokerReadinessService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/broker-readiness")
    api_response = client.get("/api/broker-readiness")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/broker_readiness.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "readiness_summary.json",
        "capability_report.json",
        "validation_report.json",
        "restriction_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "broker_readiness"
    metadata = run.result.metadata
    checks = {
        "readiness_score": 0 <= run.result.readiness.score <= 100,
        "capability_score": 0 <= run.result.capability.score <= 100,
        "validation_score": 0 <= run.result.validation.score <= 100,
        "restrictions": run.result.restrictions.status == "PASS",
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "جاهزية المراقبة الخارجية",
                "درجة الجاهزية",
                "توزيع الجاهزية",
                "نتائج القيود",
            )
        )
        and "Broker Readiness" not in template_text,
        "observation_only": metadata.get("observation_only") is True,
        "not_execution": metadata.get("not_execution") is True,
        "not_order_placement": metadata.get("not_order_placement") is True,
        "not_account_action": metadata.get("not_account_action") is True,
        "not_automation": metadata.get("not_automation") is True,
        "not_broker_control": metadata.get("not_broker_control") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
