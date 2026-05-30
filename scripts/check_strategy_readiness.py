"""Diagnostics for strategy readiness and gates."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.strategy_readiness.service import StrategyReadinessService  # noqa: E402


def main() -> None:
    run = StrategyReadinessService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/strategy-readiness")
    api_response = client.get("/api/strategy-readiness")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/strategy_readiness.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "readiness_summary.json",
        "gate_analysis.json",
        "diagnostics_report.json",
        "recommendations_report.json",
        "stability_report.json",
        "failure_analysis.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "strategy_readiness"
    checks = {
        "readiness": run.result.readiness.score >= 0,
        "gates": len(run.result.gates) == 7,
        "diagnostics": run.result.diagnostics.to_dict().get("items") is not None,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "جاهزية الاستراتيجية",
                "تقييم الجاهزية الاستراتيجية",
                "توزيع البوابات",
                "التوصيات",
            )
        )
        and "Strategy Readiness" not in template_text,
        "research_only": run.result.metadata.get("not_execution") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
