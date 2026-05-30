"""Diagnostics for the multi-timeframe confirmation engine."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.multi_timeframe.service import MultiTimeframeService  # noqa: E402


def main() -> None:
    result = MultiTimeframeService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/multi-timeframe")
    api_response = client.get("/api/multi-timeframe")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/multi_timeframe.html"
    ).read_text(encoding="utf-8")
    checks = {
        "confirmations": len(result.confirmations) > 0,
        "analytics": result.analytics["summary"]["average_alignment"] >= 0,
        "storage": all(Path(path).exists() for path in result.storage_paths.values()),
        "reports": all(Path(path).exists() for path in result.report_paths.values()),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "تأكيد الأطر الزمنية",
                "عدد الفرص المؤكدة",
                "متوسط التوافق",
                "حالات التعارض",
            )
        )
        and "Multi-Timeframe" not in template_text,
        "research_only": all(
            item.metadata.get("not_execution") is True
            for item in result.confirmations[:10]
        ),
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
