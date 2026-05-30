"""Diagnostics for the research-only trade lifecycle layer."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.trade_lifecycle.service import TradeLifecycleService  # noqa: E402


def main() -> None:
    result = TradeLifecycleService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/trade-lifecycle")
    api_response = client.get("/api/trade-lifecycle")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/trade_lifecycle.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "lifecycle_summary.json",
        "outcome_analysis.json",
        "quality_analysis.json",
        "success_analysis.json",
        "failure_analysis.json",
        "asset_analysis.json",
        "session_analysis.json",
        "confluence_analysis.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "trade_lifecycle"
    checks = {
        "records": len(result.records) > 0,
        "states": all(record.state.transitions for record in result.records[:5]),
        "analytics": result.analytics["summary"]["average_quality"] >= 0,
        "storage": all(Path(path).exists() for path in result.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "دورة حياة الفرص",
                "أفضل فرصة مكتملة",
                "توزيع النتائج",
                "أسباب الفشل",
            )
        )
        and "Trade Lifecycle" not in template_text,
        "research_only": all(
            record.metadata.get("not_execution") is True
            for record in result.records[:10]
        ),
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
