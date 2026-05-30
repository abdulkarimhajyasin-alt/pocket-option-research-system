"""Tests for Phase 27 multi-timeframe confirmation."""

from __future__ import annotations

from pathlib import Path
import shutil

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.multi_timeframe.confirmation import MultiTimeframeConfirmationEngine
from app.multi_timeframe.scoring import ConflictDetectionEngine
from app.multi_timeframe.service import MultiTimeframeService
from app.opportunity_engine.service import OpportunityService


def sample_ranking(tmp_path: Path) -> dict:
    result = OpportunityService(tmp_path).run()
    return result.rankings[0].to_dict()


def test_confirmation_engine_generates_states(tmp_path: Path) -> None:
    confirmation = MultiTimeframeConfirmationEngine().confirm(sample_ranking(tmp_path))
    assert len(confirmation.timeframe_states) == 4
    assert confirmation.confirmation_state in {
        "مؤكد بقوة",
        "مؤكد",
        "جزئي",
        "متضارب",
        "مرفوض",
    }


def test_conflict_detection_is_bounded(tmp_path: Path) -> None:
    confirmation = MultiTimeframeConfirmationEngine().confirm(sample_ranking(tmp_path))
    report = ConflictDetectionEngine().detect(list(confirmation.timeframe_states))
    assert report.severity in {"مرتفع", "متوسط", "منخفض"}
    assert report.score_penalty >= 0


def test_multi_timeframe_service_writes_reports(tmp_path: Path) -> None:
    result = MultiTimeframeService(tmp_path).run()
    assert result.analytics["summary"]["average_alignment"] >= 0
    assert all(Path(path).exists() for path in result.storage_paths.values())
    assert all(Path(path).exists() for path in result.report_paths.values())


def test_confirmations_are_research_only(tmp_path: Path) -> None:
    result = MultiTimeframeService(tmp_path).run()
    payload = result.confirmations[0].to_dict()
    assert payload["research_only"] is True
    assert payload["metadata"]["not_execution"] is True


def test_multi_timeframe_dashboard_and_api_render(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    shutil.copytree(root / "app" / "templates", app_dir / "templates")
    shutil.copytree(root / "app" / "static", app_dir / "static")
    MultiTimeframeService(tmp_path).run()
    client = TestClient(create_dashboard_app(tmp_path))
    response = client.get("/multi-timeframe")
    api_response = client.get("/api/multi-timeframe")
    assert response.status_code == 200
    assert "تأكيد الأطر الزمنية" in response.text
    assert api_response.status_code == 200
    assert api_response.json()["summary"]["average_alignment"] >= 0
