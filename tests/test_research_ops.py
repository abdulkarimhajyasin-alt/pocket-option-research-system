from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.research_ops.alerts import ResearchAlertEngine
from app.research_ops.models import RiskAssessment, StrategyStatus
from app.research_ops.recommendations import ResearchRecommendationEngine
from app.research_ops.service import ResearchOperationsService


def _strategy() -> StrategyStatus:
    return StrategyStatus(
        readiness_score=62,
        readiness_state="تحتاج تحسين كبير",
        passed_gates=2,
        warnings=5,
        failures=0,
        research_quality=62,
        confidence_stability=55,
        lifecycle_quality=61,
    )


def test_alerts_and_recommendations_are_deterministic():
    risk = RiskAssessment(severity="متوسط", risks=["ضعف الثقة"], score=70)
    alerts = ResearchAlertEngine().generate(_strategy(), risk)
    recommendations = ResearchRecommendationEngine().generate(alerts, risk)
    assert alerts
    assert recommendations
    assert all(item.title for item in recommendations)


def test_research_operations_service_generates_reports():
    run = ResearchOperationsService(Path(".")).run()
    assert run.result.executive_summary.research_health.score >= 0
    assert run.result.metadata["not_execution"] is True
    assert run.result.to_dict()["not_investment_advice"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_research_operations_dashboard_and_api_are_arabic():
    ResearchOperationsService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/research-operations")
    api = client.get("/api/research-operations")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "مركز العمليات البحثية" in page.text
    assert "ملخص العمليات البحثية" in page.text
    assert "Research Operations" not in page.text
