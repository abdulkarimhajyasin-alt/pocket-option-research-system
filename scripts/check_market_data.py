"""Diagnostics for the market data integration layer."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.market_data.analytics import MarketAnalytics  # noqa: E402
from app.market_data.providers import BaseMarketDataProvider, StaticResearchProvider  # noqa: E402
from app.market_data.service import MarketDataService  # noqa: E402


def main() -> None:
    """Run deterministic market data diagnostics."""
    provider = StaticResearchProvider()
    snapshot = provider.snapshot()
    analytics = MarketAnalytics().summarize(snapshot)
    result = MarketDataService(PROJECT_ROOT, provider=provider).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/market-data")
    api_response = client.get("/api/market-data")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/market_data.html"
    ).read_text(encoding="utf-8")
    checks = {
        "provider_contract": isinstance(provider, BaseMarketDataProvider),
        "models": bool(snapshot.assets and snapshot.sessions and snapshot.statuses),
        "analytics": analytics["summary"]["asset_count"] > 0,
        "storage": all(Path(path).exists() for path in result.storage_paths.values()),
        "reports": all(Path(path).exists() for path in result.report_paths.values()),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "بيانات السوق",
                "عدد الأصول",
                "حالة السوق",
                "جودة البيانات",
                "صحة المزود",
                "زمن الاستجابة",
                "معدل التحديث",
            )
        )
        and "Market Data" not in template_text,
        "research_only": (
            snapshot.metadata.get("research_only") is True
            and snapshot.metadata.get("no_execution") is True
            and snapshot.metadata.get("no_broker_automation") is True
        ),
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
