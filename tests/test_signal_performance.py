"""Tests for Phase 25 signal performance validation."""

from __future__ import annotations

from pathlib import Path
import shutil

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.signal_performance.confidence_validation import ConfidenceValidationEngine
from app.signal_performance.service import SignalPerformanceService


def test_signal_performance_service_generates_results(tmp_path: Path) -> None:
    result = SignalPerformanceService(tmp_path).run()
    assert result.analytics["summary"]["total_signals"] > 0
    assert result.analytics["summary"]["validation_readiness_score"] >= 0
    assert all(Path(path).exists() for path in result.storage_paths.values())
    assert all(Path(path).exists() for path in result.report_paths.values())


def test_tracked_signals_include_required_fields(tmp_path: Path) -> None:
    result = SignalPerformanceService(tmp_path).run()
    signal = result.tracked_signals[0]
    payload = signal.to_dict()
    assert payload["signal_id"]
    assert payload["asset"] == "EURUSD"
    assert payload["research_only"] is True


def test_confidence_validation_reports_balance(tmp_path: Path) -> None:
    result = SignalPerformanceService(tmp_path).run()
    report = ConfidenceValidationEngine().validate(result.paper_results)
    payload = report.to_dict()
    assert payload["assessment"] in {"ثقة متوازنة", "ثقة مفرطة", "ثقة أقل من الأداء"}
    assert "60-79" in payload["buckets"]


def test_paper_results_are_research_only(tmp_path: Path) -> None:
    result = SignalPerformanceService(tmp_path).run()
    paper = result.paper_results[0].to_dict()
    assert paper["research_only"] is True
    assert paper["no_execution"] is True


def test_signal_performance_dashboard_and_api_render(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    shutil.copytree(root / "app" / "templates", app_dir / "templates")
    shutil.copytree(root / "app" / "static", app_dir / "static")
    SignalPerformanceService(tmp_path).run()
    client = TestClient(create_dashboard_app(tmp_path))
    response = client.get("/signal-performance")
    api_response = client.get("/api/signal-performance")
    assert response.status_code == 200
    assert "أداء الإشارات" in response.text
    assert api_response.status_code == 200
    assert api_response.json()["summary"]["total_signals"] > 0
