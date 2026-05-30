"""Diagnostics for market regime research."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.market_regime.service import MarketRegimeService  # noqa: E402


def main() -> None:
    """Run market regime compliance checks."""
    run = MarketRegimeService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/market-regime")
    api_response = client.get("/api/market-regime")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/market_regime.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "regime_summary.json",
        "volatility_analysis.json",
        "trend_analysis.json",
        "transition_analysis.json",
        "compatibility_analysis.json",
        "stability_analysis.json",
        "quality_analysis.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "market_regime"
    checks = {
        "regime": bool(run.result.regime.regime_state),
        "score": 0 <= run.result.regime.regime_score <= 100,
        "volatility": 0 <= run.result.regime.volatility.score <= 100,
        "trend": 0 <= run.result.regime.trend.score <= 100,
        "compatibility": 0 <= run.result.compatibility.score <= 100,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "محرك حالة السوق",
                "الوضع الحالي للسوق",
                "توزيع حالات السوق",
                "تحليل التوافق",
            )
        )
        and "Market Regime" not in template_text,
        "research_only": run.result.metadata.get("not_execution") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
