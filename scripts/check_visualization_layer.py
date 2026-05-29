"""Diagnostics for Phase 17 dashboard visualization services."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.analytics import DashboardAnalyticsService  # noqa: E402
from app.dashboard.metrics import DashboardMetricsService  # noqa: E402
from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.i18n import get_translations  # noqa: E402


def main() -> None:
    """Run deterministic visualization diagnostics."""
    translations = get_translations("ar")
    analytics = DashboardAnalyticsService(PROJECT_ROOT)
    metrics = DashboardMetricsService(PROJECT_ROOT)
    app = create_dashboard_app(PROJECT_ROOT)
    routes = {route.path for route in app.routes}
    required_routes = {
        "/signals",
        "/api/dashboard",
        "/api/metrics",
        "/api/validation",
        "/api/datasets",
        "/api/signals",
    }
    workbench = metrics.workbench()
    signal_analytics = analytics.signal_analytics()
    validation_analytics = analytics.validation_analytics()
    dataset_analytics = analytics.dataset_analytics()
    equity_analytics = analytics.equity_analytics()
    summary = {
        "arabic_loaded": translations["nav"]["signals"] == "الإشارات",
        "missing_routes": sorted(required_routes - routes),
        "metrics": len(workbench["metrics"]),
        "insights": len(workbench["insights"]),
        "signal_chart": bool(signal_analytics["distribution"]["labels"]),
        "validation_chart": "history" in validation_analytics,
        "dataset_chart": "quality" in dataset_analytics,
        "equity_chart": "equity" in equity_analytics,
    }
    print(summary)
    if (
        not summary["arabic_loaded"]
        or summary["missing_routes"]
        or summary["metrics"] < 8
        or not summary["validation_chart"]
        or not summary["dataset_chart"]
        or not summary["equity_chart"]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
