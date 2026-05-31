"""Diagnostics for the local paper-only execution engine."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.paper_execution.models import (  # noqa: E402
    RISK_FAIL,
    RISK_PASS,
    RISK_WARNING,
    STATUS_ACCEPTED,
    STATUS_ACTIVE,
    STATUS_BREAKEVEN,
    STATUS_CANCELLED,
    STATUS_CREATED,
    STATUS_EXPIRED,
    STATUS_LOSS,
    STATUS_REJECTED,
    STATUS_WIN,
)
from app.paper_execution.service import PaperExecutionService  # noqa: E402


def main() -> None:
    """Run paper execution compliance checks."""
    run = PaperExecutionService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/paper-execution")
    api_response = client.get("/api/paper-execution")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/paper_execution.html"
    ).read_text(encoding="utf-8")
    allowed_status = {
        STATUS_CREATED,
        STATUS_ACCEPTED,
        STATUS_REJECTED,
        STATUS_ACTIVE,
        STATUS_EXPIRED,
        STATUS_WIN,
        STATUS_LOSS,
        STATUS_BREAKEVEN,
        STATUS_CANCELLED,
    }
    required_reports = {
        "paper_execution_summary.json",
        "orders_report.json",
        "lifecycle_report.json",
        "results_report.json",
        "risk_report.json",
        "analytics_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    required_storage = {
        "paper_orders.json",
        "paper_lifecycle.json",
        "paper_results.json",
        "risk_results.json",
        "analytics.json",
        "diagnostics.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "paper_execution"
    storage_dir = PROJECT_ROOT / "storage" / "paper_execution"
    metadata = run.result.metadata
    checks = {
        "orders": len(run.result.orders) >= 5,
        "statuses": all(item.status in allowed_status for item in run.result.orders),
        "lifecycle": len(run.result.lifecycle) >= len(run.result.orders),
        "results": len(run.result.results) >= 1,
        "risk": all(
            item.status in {RISK_PASS, RISK_WARNING, RISK_FAIL}
            for item in run.result.risk_gates
        ),
        "score": 0 <= run.result.score <= 100,
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
                "محرك التنفيذ الورقي",
                "تنفيذ ورقي",
                "إجمالي الأوامر الورقية",
                "توزيع الأوامر الورقية",
                "المخاطر الورقية",
            )
        )
        and "Paper Execution" not in template_text,
        "paper_only": metadata.get("paper_only") is True,
        "research_only": metadata.get("research_only") is True,
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
