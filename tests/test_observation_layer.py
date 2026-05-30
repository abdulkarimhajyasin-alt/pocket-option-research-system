"""Tests for Phase 21 broker observation layer."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import shutil

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.observation.analytics import ObservationAnalytics
from app.observation.models import AssetObservation, PayoutObservation
from app.observation.provider import MockObservationProvider
from app.observation.service import ObservationService


def test_observation_models_validate_common_fields() -> None:
    timestamp = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    asset = AssetObservation(
        timestamp=timestamp,
        asset="EURUSD",
        timeframe="1m",
        source="unit",
        activity_score=75,
    )
    payout = PayoutObservation(
        timestamp=timestamp,
        asset="EURUSD",
        timeframe="1m",
        source="unit",
        payout_percent=82,
    )
    assert asset.to_dict()["asset"] == "EURUSD"
    assert payout.to_dict()["payout_percent"] == 82


def test_mock_provider_generates_snapshot() -> None:
    provider = MockObservationProvider()
    snapshot = provider.get_market_snapshot()
    assert snapshot.metadata["no_broker_interaction"] is True
    assert len(snapshot.assets) >= 4
    assert len(snapshot.candles) > 0


def test_observation_analytics_are_deterministic() -> None:
    provider = MockObservationProvider()
    analytics = ObservationAnalytics().summarize(provider.get_market_snapshot())
    assert analytics["active_assets"] == 4
    assert analytics["average_payout"] == 74.2
    assert analytics["assessment"]["readiness"] in {
        "فرص مراقبة جيدة",
        "مراقبة إضافية مطلوبة",
        "بيانات غير كافية",
    }


def test_observation_service_writes_storage_and_reports(tmp_path: Path) -> None:
    result = ObservationService(tmp_path, provider=MockObservationProvider()).run()
    assert result.analytics["observation_count"] > 0
    assert all(Path(path).exists() for path in result.storage_paths.values())
    assert all(Path(path).exists() for path in result.report_paths.values())


def test_observation_dashboard_and_api_render(tmp_path: Path) -> None:
    templates_src = Path(__file__).resolve().parents[1] / "app" / "templates"
    static_src = Path(__file__).resolve().parents[1] / "app" / "static"
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    shutil.copytree(templates_src, app_dir / "templates")
    shutil.copytree(static_src, app_dir / "static")
    ObservationService(tmp_path, provider=MockObservationProvider()).run()

    client = TestClient(create_dashboard_app(tmp_path))
    response = client.get("/observation")
    api_response = client.get("/api/observation")
    assert response.status_code == 200
    assert "مراقبة السوق" in response.text
    assert api_response.status_code == 200
    assert api_response.json()["summary"]["observation_count"] > 0
