"""Diagnostics for paper-only portfolio governance."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.paper_portfolio.models import FAIL, PASS, WARNING  # noqa: E402
from app.paper_portfolio.service import PaperPortfolioService  # noqa: E402


def main() -> None:
    """Run paper portfolio compliance checks."""
    run = PaperPortfolioService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/paper-portfolio")
    api_response = client.get("/api/paper-portfolio")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/paper_portfolio.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "portfolio_summary.json",
        "exposure_report.json",
        "drawdown_report.json",
        "governance_report.json",
        "limits_report.json",
        "analytics_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    required_storage = {
        "portfolio_results.json",
        "exposure_results.json",
        "drawdown_results.json",
        "governance_results.json",
        "limits_results.json",
        "diagnostics.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "paper_portfolio"
    storage_dir = PROJECT_ROOT / "storage" / "paper_portfolio"
    metadata = run.result.metadata
    checks = {
        "portfolio": run.result.portfolio.total_orders >= 0,
        "score": 0 <= run.result.score <= 100,
        "health": 0 <= run.result.portfolio.health_score <= 100,
        "stability": 0 <= run.result.portfolio.stability_score <= 100,
        "risk": 0 <= run.result.portfolio.risk_score <= 100,
        "exposure": 0 <= run.result.exposure.get("exposure_score", 0) <= 100,
        "drawdown": 0 <= run.result.drawdown.get("drawdown_score", 0) <= 100,
        "governance": all(item.status in {PASS, WARNING, FAIL} for item in run.result.governance),
        "limits": all(item.status in {PASS, WARNING, FAIL} for item in run.result.limits),
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
                "إدارة المحفظة الورقية",
                "المحفظة الورقية",
                "إجمالي الأوامر",
                "الأداء الورقي",
                "الحوكمة",
            )
        )
        and "Paper Portfolio" not in template_text,
        "paper_only": metadata.get("paper_only") is True,
        "research_only": metadata.get("research_only") is True,
        "not_real_execution": metadata.get("not_real_execution") is True,
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
