"""Diagnostics for the live market feed layer."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.live_feed.analytics import LiveFeedAnalytics  # noqa: E402
from app.live_feed.provider import MarketFeedProvider, MockLiveFeedProvider  # noqa: E402
from app.live_feed.service import LiveFeedService  # noqa: E402


def main() -> None:
    """Run deterministic live-feed diagnostics."""
    provider = MockLiveFeedProvider()
    provider.connect()
    snapshot = provider.get_latest()
    analytics = LiveFeedAnalytics().summarize(snapshot)
    result = LiveFeedService(PROJECT_ROOT, provider=provider).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/live-feed")
    api_response = client.get("/api/live-feed")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/live_feed.html"
    ).read_text(encoding="utf-8")
    checks = {
        "feed_providers": isinstance(provider, MarketFeedProvider),
        "feed_health": analytics["summary"]["health_label"] in {
            "ممتاز",
            "جيد",
            "متوسط",
            "ضعيف",
        },
        "feed_analytics": analytics["summary"]["update_count"] > 0,
        "report_generation": all(Path(path).exists() for path in result.report_paths.values()),
        "storage_generation": all(Path(path).exists() for path in result.storage_paths.values()),
        "dashboard_integration": (
            response.status_code == 200 and api_response.status_code == 200
        ),
        "arabic_dashboard_compliance": all(
            label in (template_text + response.text)
            for label in (
                "البث المباشر",
                "حالة البث",
                "زمن الاستجابة",
                "الأصول النشطة",
                "عدد التحديثات",
                "صحة البث",
                "معدل التحديث",
            )
        )
        and "Live Update Frequency" not in template_text,
        "local_only": snapshot.metadata.get("no_broker_connection") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
