"""Diagnostics for the opportunity qualification engine."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.opportunity_engine.service import OpportunityService  # noqa: E402


def main() -> None:
    result = OpportunityService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/opportunities")
    api_response = client.get("/api/opportunities")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/opportunities.html"
    ).read_text(encoding="utf-8")
    checks = {
        "opportunities": len(result.opportunities) > 0,
        "rankings": result.rankings[0].rank == 1 if result.rankings else False,
        "analytics": result.analytics["summary"]["opportunity_count"] > 0,
        "storage": all(Path(path).exists() for path in result.storage_paths.values()),
        "reports": all(Path(path).exists() for path in result.report_paths.values()),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "الفرص المؤهلة",
                "أفضل فرصة حالية",
                "عدد الفرص",
                "أعلى درجة",
                "حالة التأهيل",
            )
        )
        and "Opportunity" not in template_text,
        "research_only": all(
            item.metadata.get("not_execution") is True
            for item in result.opportunities[:10]
        ),
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
