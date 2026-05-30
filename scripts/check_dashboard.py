"""Diagnostics for the local research dashboard layer."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.actions import ACTION_DEFINITIONS  # noqa: E402
from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.dashboard.service import DashboardService  # noqa: E402


def main() -> None:
    """Run deterministic dashboard diagnostics."""
    service = DashboardService(PROJECT_ROOT)
    app = create_dashboard_app(PROJECT_ROOT)
    route_paths = {route.path for route in app.routes}
    required_routes = {
        "/",
        "/strategies",
        "/datasets",
        "/validation",
        "/signals",
        "/reports",
        "/execution",
        "/observation",
        "/live-feed",
        "/market-data",
        "/signals-intelligence",
        "/signal-performance",
        "/opportunities",
        "/multi-timeframe",
        "/confluence",
        "/trade-lifecycle",
        "/actions",
    }
    missing_routes = sorted(required_routes - route_paths)
    templates = [
        PROJECT_ROOT / "app/templates/dashboard/base.html",
        PROJECT_ROOT / "app/templates/dashboard/overview.html",
        PROJECT_ROOT / "app/templates/dashboard/execution.html",
        PROJECT_ROOT / "app/templates/dashboard/observation.html",
        PROJECT_ROOT / "app/templates/dashboard/live_feed.html",
        PROJECT_ROOT / "app/templates/dashboard/market_data.html",
        PROJECT_ROOT / "app/templates/dashboard/signals_intelligence.html",
        PROJECT_ROOT / "app/templates/dashboard/signal_performance.html",
        PROJECT_ROOT / "app/templates/dashboard/opportunities.html",
        PROJECT_ROOT / "app/templates/dashboard/multi_timeframe.html",
        PROJECT_ROOT / "app/templates/dashboard/confluence.html",
        PROJECT_ROOT / "app/templates/dashboard/trade_lifecycle.html",
        PROJECT_ROOT / "app/templates/dashboard/actions.html",
    ]
    static_assets = [
        PROJECT_ROOT / "app/static/dashboard/dashboard.css",
        PROJECT_ROOT / "app/static/dashboard/dashboard.js",
    ]
    reports = service.report_loader.list_reports()
    overview = service.overview()
    summary = {
        "routes_ok": not missing_routes,
        "missing_routes": missing_routes,
        "service_ok": True,
        "reports_found": len(reports),
        "actions": sorted(ACTION_DEFINITIONS),
        "templates_ok": all(path.exists() for path in templates),
        "static_ok": all(path.exists() for path in static_assets),
        "strategies": len(overview.strategies),
        "datasets": len(overview.datasets),
        "validations": len(overview.validations),
    }
    print(summary)
    if (
        missing_routes
        or not summary["templates_ok"]
        or not summary["static_ok"]
        or not ACTION_DEFINITIONS
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
