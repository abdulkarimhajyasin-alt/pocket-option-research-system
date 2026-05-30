"""Diagnostics for the signal performance layer."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.signal_performance.service import SignalPerformanceService  # noqa: E402


def main() -> None:
    result = SignalPerformanceService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/signal-performance")
    api_response = client.get("/api/signal-performance")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/signal_performance.html"
    ).read_text(encoding="utf-8")
    checks = {
        "tracked_signals": len(result.tracked_signals) > 0,
        "paper_results": len(result.paper_results) > 0,
        "analytics": result.analytics["summary"]["total_signals"] > 0,
        "storage": all(Path(path).exists() for path in result.storage_paths.values()),
        "reports": all(Path(path).exists() for path in result.report_paths.values()),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "أداء الإشارات",
                "ملخص الأداء البحثي",
                "إجمالي الإشارات",
                "نسبة النجاح",
                "درجة الجاهزية البحثية",
            )
        )
        and "Signal Performance" not in template_text,
        "research_only": all(
            item.signal.metadata.get("not_execution") is True
            for item in result.paper_results[:10]
        ),
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
