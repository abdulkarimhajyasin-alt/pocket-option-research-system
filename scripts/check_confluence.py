"""Diagnostics for the confluence research engine."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.confluence.service import ConfluenceService  # noqa: E402
from app.dashboard.routes import create_dashboard_app  # noqa: E402


def main() -> None:
    result = ConfluenceService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/confluence")
    api_response = client.get("/api/confluence")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/confluence.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "confluence_summary.json",
        "factor_analysis.json",
        "asset_confluence.json",
        "session_confluence.json",
        "timeframe_confluence.json",
        "rejection_analysis.json",
        "decision_summary.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "confluence"
    checks = {
        "decisions": len(result.decisions) > 0,
        "factor_scores": all(
            len(item.confluence.factors) == 6 for item in result.decisions[:5]
        ),
        "analytics": result.analytics["summary"]["average_confluence"] >= 0,
        "storage": all(Path(path).exists() for path in result.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "محرك التوافق",
                "أفضل فرصة متوافقة",
                "درجة التوافق",
                "عوامل التوافق",
            )
        )
        and "Confluence" not in template_text,
        "research_only": all(
            item.confluence.metadata.get("not_execution") is True
            for item in result.decisions[:10]
        ),
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
