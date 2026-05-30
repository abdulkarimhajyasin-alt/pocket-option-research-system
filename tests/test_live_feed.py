"""Tests for Phase 22 live market feed layer."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import shutil

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.live_feed.analytics import LiveFeedAnalytics
from app.live_feed.buffer import FeedBuffer
from app.live_feed.models import CandleUpdate, TickData
from app.live_feed.provider import MockLiveFeedProvider
from app.live_feed.service import LiveFeedService


def test_live_feed_models_validate() -> None:
    timestamp = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    tick = TickData(
        timestamp=timestamp,
        source="unit",
        asset="EURUSD",
        timeframe="tick",
        bid=1.0,
        ask=1.0001,
        price=1.00005,
    )
    candle = CandleUpdate(
        timestamp=timestamp,
        source="unit",
        asset="EURUSD",
        timeframe="1m",
        open=1.0,
        high=1.001,
        low=0.999,
        close=1.0005,
    )
    assert tick.to_dict()["asset"] == "EURUSD"
    assert candle.to_dict()["timeframe"] == "1m"


def test_mock_live_feed_provider_simulates_updates() -> None:
    provider = MockLiveFeedProvider()
    assert provider.connect() is True
    snapshot = provider.get_latest()
    assert snapshot.metadata["no_broker_connection"] is True
    assert len(snapshot.ticks) > 0
    assert len(snapshot.candles) > 0


def test_feed_buffer_retains_latest_updates() -> None:
    provider = MockLiveFeedProvider()
    snapshot = provider.get_latest()
    buffer = FeedBuffer(tick_retention=3, candle_retention=2)
    buffer.update_snapshot(snapshot)
    assert buffer.latest_snapshot() == snapshot
    assert len(buffer.ticks("EURUSD")) == 3
    assert "EURUSD" in buffer.active_assets()


def test_live_feed_analytics_and_reports(tmp_path: Path) -> None:
    result = LiveFeedService(tmp_path, provider=MockLiveFeedProvider()).run()
    analytics = LiveFeedAnalytics().summarize(result.snapshot)
    assert analytics["summary"]["update_count"] > 0
    assert analytics["summary"]["readiness"] in {
        "جاهز",
        "مستقر",
        "يحتاج مراقبة",
        "غير مستقر",
    }
    assert all(Path(path).exists() for path in result.report_paths.values())
    assert all(Path(path).exists() for path in result.storage_paths.values())


def test_live_feed_dashboard_and_api_render(tmp_path: Path) -> None:
    templates_src = Path(__file__).resolve().parents[1] / "app" / "templates"
    static_src = Path(__file__).resolve().parents[1] / "app" / "static"
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    shutil.copytree(templates_src, app_dir / "templates")
    shutil.copytree(static_src, app_dir / "static")
    LiveFeedService(tmp_path, provider=MockLiveFeedProvider()).run()

    client = TestClient(create_dashboard_app(tmp_path))
    response = client.get("/live-feed")
    api_response = client.get("/api/live-feed")
    assert response.status_code == 200
    assert "البث المباشر" in response.text
    assert api_response.status_code == 200
    assert api_response.json()["summary"]["update_count"] > 0
