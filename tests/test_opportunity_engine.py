"""Tests for Phase 26 opportunity qualification engine."""

from __future__ import annotations

from pathlib import Path
import shutil

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.opportunity_engine.qualification import OpportunityQualificationEngine
from app.opportunity_engine.service import OpportunityService
from app.opportunity_engine.structure_score import StructureScoreEngine
from app.signal_intelligence.service import SignalIntelligenceService


def sample_signal(tmp_path: Path) -> dict:
    result = SignalIntelligenceService(tmp_path).run()
    return result.snapshot.signals[-1].to_dict()


def test_structure_score_engine_is_bounded(tmp_path: Path) -> None:
    score = StructureScoreEngine().score(sample_signal(tmp_path))
    assert 0 <= score.score <= 100
    assert score.explanation


def test_qualification_engine_generates_state(tmp_path: Path) -> None:
    opportunity = OpportunityQualificationEngine().qualify(sample_signal(tmp_path))
    assert 0 <= opportunity.qualification_score <= 100
    assert opportunity.qualification_state in {
        "مؤهلة جدا",
        "مؤهلة",
        "متوسطة",
        "ضعيفة",
        "مرفوضة",
    }
    assert opportunity.metadata["research_only"] is True


def test_opportunity_service_writes_reports(tmp_path: Path) -> None:
    result = OpportunityService(tmp_path).run()
    assert result.analytics["summary"]["opportunity_count"] > 0
    assert result.rankings[0].rank == 1
    assert all(Path(path).exists() for path in result.storage_paths.values())
    assert all(Path(path).exists() for path in result.report_paths.values())


def test_rankings_are_descending(tmp_path: Path) -> None:
    result = OpportunityService(tmp_path).run()
    scores = [item.opportunity.qualification_score for item in result.rankings]
    assert scores == sorted(scores, reverse=True)


def test_opportunities_dashboard_and_api_render(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    shutil.copytree(root / "app" / "templates", app_dir / "templates")
    shutil.copytree(root / "app" / "static", app_dir / "static")
    OpportunityService(tmp_path).run()
    client = TestClient(create_dashboard_app(tmp_path))
    response = client.get("/opportunities")
    api_response = client.get("/api/opportunities")
    assert response.status_code == 200
    assert "الفرص المؤهلة" in response.text
    assert api_response.status_code == 200
    assert api_response.json()["summary"]["opportunity_count"] > 0
