"""Tests for Phase 24 signal intelligence layer."""

from __future__ import annotations

from pathlib import Path
import shutil

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.data.csv_loader import CsvCandleLoader
from app.signal_intelligence.confidence import ConfidenceEngine
from app.signal_intelligence.service import SignalIntelligenceService
from app.signal_intelligence.structure import StructureEngine


def load_sample():
    root = Path(__file__).resolve().parents[1]
    return CsvCandleLoader().load(root / "data" / "sample_eurusd_m1.csv", "EURUSD", "1m")


def test_structure_engine_detects_state() -> None:
    candles = load_sample()
    state = StructureEngine().detect(list(candles.history_until(10)))
    assert state.state in {"هيكل صاعد", "هيكل هابط", "هيكل عرضي", "هيكل انتقالي"}
    assert state.confidence_contribution >= 0


def test_confidence_engine_range() -> None:
    service = SignalIntelligenceService(Path(__file__).resolve().parents[1])
    candles = load_sample()
    history = list(candles.history_until(8))
    structure = service.structure.detect(history)
    cisd = service.cisd.detect(history)
    fvg = service.fvg.detect(history)
    ifvg = service.ifvg.detect(history, fvg)
    liquidity = service.liquidity.detect(history)
    session = service.sessions.detect(history[-1])
    confidence = ConfidenceEngine().score(structure, cisd, fvg, ifvg, liquidity, session)
    assert 0 <= confidence.score <= 100
    assert confidence.classification in {"ضعيفة", "متوسطة", "قوية", "عالية الاقتناع"}


def test_signal_intelligence_service_reports(tmp_path: Path) -> None:
    result = SignalIntelligenceService(tmp_path).run()
    assert result.analytics["summary"]["signal_count"] > 0
    assert result.analytics["summary"]["highest_confidence"] <= 100
    assert all(Path(path).exists() for path in result.storage_paths.values())
    assert all(Path(path).exists() for path in result.report_paths.values())


def test_signal_intelligence_classifications_are_research_only(tmp_path: Path) -> None:
    result = SignalIntelligenceService(tmp_path).run()
    latest = result.analytics["latest_signals"]
    assert latest
    assert all(signal["research_only"] is True for signal in latest)
    assert all(signal["metadata"]["not_execution"] is True for signal in latest)


def test_signal_intelligence_dashboard_and_api_render(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    shutil.copytree(root / "app" / "templates", app_dir / "templates")
    shutil.copytree(root / "app" / "static", app_dir / "static")
    SignalIntelligenceService(tmp_path).run()
    client = TestClient(create_dashboard_app(tmp_path))
    response = client.get("/signals-intelligence")
    api_response = client.get("/api/signals-intelligence")
    assert response.status_code == 200
    assert "ذكاء الإشارات" in response.text
    assert api_response.status_code == 200
    assert api_response.json()["summary"]["signal_count"] > 0
