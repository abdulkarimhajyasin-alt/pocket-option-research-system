"""Tests for Phase 23 market data integration layer."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import shutil

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.market_data.analytics import MarketAnalytics
from app.market_data.models import MarketAsset, MarketCandle
from app.market_data.providers import StaticResearchProvider
from app.market_data.service import MarketDataService


def test_market_data_models_validate() -> None:
    timestamp = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    asset = MarketAsset(
        timestamp=timestamp,
        provider="unit",
        asset="EURUSD",
        timeframe="1m",
        quality_score=90,
    )
    candle = MarketCandle(
        timestamp=timestamp,
        provider="unit",
        asset="EURUSD",
        timeframe="1m",
        open=1.0,
        high=1.001,
        low=0.999,
        close=1.0005,
    )
    assert asset.to_dict()["asset"] == "EURUSD"
    assert candle.to_dict()["close"] == 1.0005


def test_static_research_provider_snapshot_is_research_only() -> None:
    provider = StaticResearchProvider()
    snapshot = provider.snapshot()
    assert snapshot.metadata["research_only"] is True
    assert snapshot.metadata["no_execution"] is True
    assert len(snapshot.assets) >= 5
    assert len(snapshot.latencies) > 0


def test_market_analytics_scores_readiness() -> None:
    analytics = MarketAnalytics().summarize(StaticResearchProvider().snapshot())
    assert analytics["summary"]["asset_count"] == 6
    assert analytics["summary"]["readiness_score"] > 0
    assert analytics["summary"]["readiness_label"] in {
        "جاهز للبحث",
        "مستقر للبحث",
        "يحتاج مراقبة",
        "غير جاهز",
    }


def test_market_data_service_writes_storage_and_reports(tmp_path: Path) -> None:
    result = MarketDataService(tmp_path, provider=StaticResearchProvider()).run()
    assert result.analytics["summary"]["asset_count"] == 6
    assert all(Path(path).exists() for path in result.storage_paths.values())
    assert all(Path(path).exists() for path in result.report_paths.values())


def test_market_data_dashboard_and_api_render(tmp_path: Path) -> None:
    templates_src = Path(__file__).resolve().parents[1] / "app" / "templates"
    static_src = Path(__file__).resolve().parents[1] / "app" / "static"
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    shutil.copytree(templates_src, app_dir / "templates")
    shutil.copytree(static_src, app_dir / "static")
    MarketDataService(tmp_path, provider=StaticResearchProvider()).run()

    client = TestClient(create_dashboard_app(tmp_path))
    response = client.get("/market-data")
    api_response = client.get("/api/market-data")
    assert response.status_code == 200
    assert "بيانات السوق" in response.text
    assert api_response.status_code == 200
    assert api_response.json()["summary"]["asset_count"] == 6
