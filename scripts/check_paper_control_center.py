"""Diagnostics for the paper-only trading control center."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.paper_control_center.models import FAIL, PASS, WARNING  # noqa: E402
from app.paper_control_center.service import PaperControlCenterService  # noqa: E402


def main() -> None:
    """Run paper control center compliance checks."""
    run = PaperControlCenterService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/paper-control")
    api_response = client.get("/api/paper-control")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/paper_control.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "control_center_summary.json",
        "health_report.json",
        "monitoring_report.json",
        "governance_report.json",
        "decision_report.json",
        "analytics_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    required_storage = {
        "control_center_results.json",
        "health_results.json",
        "monitoring_results.json",
        "governance_results.json",
        "decision_results.json",
        "diagnostics.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "paper_control_center"
    storage_dir = PROJECT_ROOT / "storage" / "paper_control_center"
    metadata = run.result.metadata
    checks = {
        "control": 0 <= run.result.control.overall_score <= 100,
        "health": 0 <= run.result.health.get("health_score", 0) <= 100,
        "monitoring": 0 <= run.result.monitoring.get("monitoring_score", 0) <= 100,
        "governance": all(item.status in {PASS, WARNING, FAIL} for item in run.result.governance),
        "decision": run.result.decision.get("research_recommendation_only") is True,
        "storage_paths": all(Path(path).exists() for path in run.storage_paths.values()),
        "report_paths": all(Path(path).exists() for path in run.report_paths.values()),
        "storage_files": required_storage.issubset(
            {path.name for path in storage_dir.glob("*.json")}
        ),
        "report_files": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "مركز التحكم بالتداول الورقي",
                "مركز التحكم الورقي",
                "الصحة العامة",
                "القرار الحالي",
                "التنفيذ الورقي",
            )
        )
        and "Paper Control" not in template_text,
        "paper_only": metadata.get("paper_only") is True,
        "research_only": metadata.get("research_only") is True,
        "recommendation_only": metadata.get("recommendation_only") is True,
        "not_control_action": metadata.get("not_control_action") is True,
        "not_real_execution": metadata.get("not_real_execution") is True,
        "not_real_order_placement": metadata.get("not_real_order_placement") is True,
        "not_broker_access": metadata.get("not_broker_access") is True,
        "not_account_login": metadata.get("not_account_login") is True,
        "not_authentication": metadata.get("not_authentication") is True,
        "not_credential_handling": metadata.get("not_credential_handling") is True,
        "not_browser_automation": metadata.get("not_browser_automation") is True,
        "not_real_money": metadata.get("not_real_money") is True,
        "not_position_management": metadata.get("not_position_management") is True,
        "not_trading_automation": metadata.get("not_trading_automation") is True,
        "not_broker_control": metadata.get("not_broker_control") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
