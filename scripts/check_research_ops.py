"""Diagnostics for research operations control center."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.research_ops.service import ResearchOperationsService  # noqa: E402


def main() -> None:
    run = ResearchOperationsService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/research-operations")
    api_response = client.get("/api/research-operations")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/research_operations.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "executive_report.json",
        "health_report.json",
        "alerts_report.json",
        "recommendations_report.json",
        "risk_report.json",
        "operations_summary.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "research_ops"
    checks = {
        "summary": run.result.executive_summary.research_health.score >= 0,
        "alerts": len(run.result.alerts) >= 0,
        "recommendations": len(run.result.recommendations) > 0,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "مركز العمليات البحثية",
                "ملخص العمليات البحثية",
                "صحة النظام البحثي",
                "الإجراء التالي",
            )
        )
        and "Research Operations" not in template_text,
        "research_only": run.result.metadata.get("not_execution") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
