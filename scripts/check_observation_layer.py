"""Diagnostics for the broker observation layer."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.observation.analytics import ObservationAnalytics  # noqa: E402
from app.observation.provider import MockObservationProvider, ObservationProvider  # noqa: E402
from app.observation.service import ObservationService  # noqa: E402


def main() -> None:
    """Run deterministic observation diagnostics."""
    provider = MockObservationProvider()
    snapshot = provider.get_market_snapshot()
    analytics = ObservationAnalytics().summarize(snapshot)
    result = ObservationService(PROJECT_ROOT, provider=provider).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response_text = client.get("/observation").text
    route_paths = {route.path for route in app.routes}
    template = PROJECT_ROOT / "app/templates/dashboard/observation.html"
    template_text = template.read_text(encoding="utf-8")
    checks = {
        "observation_models": bool(snapshot.assets and snapshot.payouts and snapshot.sessions),
        "provider_registration": isinstance(provider, ObservationProvider),
        "analytics_generation": analytics["observation_count"] > 0,
        "report_generation": all(Path(path).exists() for path in result.report_paths.values()),
        "dashboard_integration": (
            "/observation" in route_paths
            and "/api/observation" in route_paths
            and response_text
            and client.get("/api/observation").status_code == 200
        ),
        "arabic_dashboard_compliance": all(
            label in (template_text + response_text)
            for label in (
                "مراقبة السوق",
                "الأصول النشطة",
                "متوسط العائد",
                "نشاط السوق",
                "عدد الملاحظات",
            )
        )
        and "Most Active Assets" not in template_text,
        "local_only": snapshot.metadata.get("no_broker_interaction") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
