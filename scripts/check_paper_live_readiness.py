"""Diagnostics for the readiness-only paper-to-live gate."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.paper_live_readiness.models import FAIL, PASS, WARNING  # noqa: E402
from app.paper_live_readiness.service import PaperToLiveReadinessService  # noqa: E402


def main() -> None:
    """Run readiness gate compliance checks."""
    run = PaperToLiveReadinessService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/paper-live-readiness")
    api_response = client.get("/api/paper-live-readiness")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/paper_live_readiness.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "readiness_summary.json",
        "gate_report.json",
        "safety_report.json",
        "maturity_report.json",
        "stability_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    required_storage = {
        "readiness_results.json",
        "gate_results.json",
        "safety_results.json",
        "maturity_results.json",
        "stability_results.json",
        "diagnostics.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "paper_live_readiness"
    storage_dir = PROJECT_ROOT / "storage" / "paper_live_readiness"
    metadata = run.result.metadata
    checks = {
        "readiness": 0 <= run.result.readiness.overall_score <= 100,
        "safety": run.result.safety.get("status") == PASS,
        "maturity": 0 <= run.result.maturity.get("maturity_score", 0) <= 100,
        "stability": 0 <= run.result.stability.get("stability_score", 0) <= 100,
        "gates": all(item.status in {PASS, WARNING, FAIL} for item in run.result.gates),
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
                "بوابة الجاهزية للمرحلة التالية",
                "جاهزية المرحلة التالية",
                "توزيع الجاهزية",
                "نتائج البوابات",
                "السلامة",
                "التوصيات",
            )
        )
        and "Paper-to-Live" not in template_text,
        "readiness_only": metadata.get("readiness_only") is True,
        "paper_only": metadata.get("paper_only") is True,
        "research_only": metadata.get("research_only") is True,
        "not_execution": metadata.get("not_execution") is True,
        "not_real_execution": metadata.get("not_real_execution") is True,
        "not_order_placement": metadata.get("not_order_placement") is True,
        "not_live_trading": metadata.get("not_live_trading") is True,
        "not_broker_access": metadata.get("not_broker_access") is True,
        "not_broker_api": metadata.get("not_broker_api") is True,
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
