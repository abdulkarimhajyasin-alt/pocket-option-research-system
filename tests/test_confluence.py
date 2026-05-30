from pathlib import Path

from fastapi.testclient import TestClient

from app.confluence.confluence import ConfluenceEngine, ResearchDecisionEngine
from app.confluence.service import ConfluenceService
from app.dashboard.routes import create_dashboard_app


def test_confluence_engine_combines_all_factors():
    opportunity = {
        "opportunity_id": "research-1",
        "asset": "EURUSD",
        "classification": "تصنيف صعودي",
        "confidence": 78,
        "qualification_score": 72,
        "timestamp": "2026-05-30T10:00:00",
        "liquidity_score": 68,
        "session_score": 74,
        "supporting_factors": ["جلسة لندن", "سيولة مؤكدة"],
        "rejection_factors": [],
        "qualification_state": "قوية",
        "strengths": ["هيكل داعم"],
        "weaknesses": [],
    }
    confirmation = {
        "confirmation_score": 76,
        "confirmation_state": "مؤكد",
        "session": "جلسة لندن",
        "supporting_factors": ["توافق زمني"],
        "conflicting_factors": [],
        "conflict": {"has_conflict": False},
    }
    confluence = ConfluenceEngine().evaluate(
        opportunity=opportunity,
        confirmation=confirmation,
        signal_summary={
            "average_confidence": 70,
            "classification_balance_score": 66,
        },
        performance_summary={
            "win_rate": 0.58,
            "stability_score": 67,
            "consistency_score": 70,
            "confidence_accuracy_score": 85,
        },
        session_performance={"جلسة لندن": 0.61},
    )
    assert 0 <= confluence.score <= 100
    assert len(confluence.factors) == 6
    assert confluence.metadata["not_execution"] is True


def test_research_decision_is_not_execution_recommendation():
    service = ConfluenceService(Path("."))
    result = service.run()
    assert result.decisions
    first = result.decisions[0]
    assert first.to_dict()["not_execution"] is True
    assert "شراء" not in first.final_decision
    assert "بيع" not in first.final_decision
    assert ResearchDecisionEngine().decide(first.confluence).to_dict()["research_only"]


def test_confluence_storage_and_reports_are_generated():
    result = ConfluenceService(Path(".")).run()
    assert all(Path(path).exists() for path in result.storage_paths.values())
    assert all(Path(path).exists() for path in result.report_paths.values())
    assert "factor_contribution" in result.analytics
    assert "best_decision" in result.analytics


def test_confluence_dashboard_and_api_are_arabic():
    ConfluenceService(Path(".")).run()
    app = create_dashboard_app(Path("."))
    client = TestClient(app)
    page = client.get("/confluence")
    api = client.get("/api/confluence")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "محرك التوافق" in page.text
    assert "أفضل فرصة متوافقة" in page.text
    assert "Confluence" not in page.text
