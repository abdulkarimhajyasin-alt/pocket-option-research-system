from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.paper_portfolio.models import FAIL, PASS, WARNING
from app.paper_portfolio.service import PaperPortfolioService


def test_paper_portfolio_service_generates_outputs() -> None:
    run = PaperPortfolioService(Path(".")).run()

    assert 0 <= run.result.score <= 100
    assert 0 <= run.result.portfolio.health_score <= 100
    assert 0 <= run.result.portfolio.stability_score <= 100
    assert 0 <= run.result.portfolio.risk_score <= 100
    assert run.result.metadata["paper_only"] is True
    assert run.result.metadata["research_only"] is True
    assert run.result.metadata["not_real_execution"] is True
    assert run.result.metadata["not_real_money"] is True
    assert run.result.metadata["not_broker_access"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_paper_portfolio_governance_and_limits_are_bounded() -> None:
    run = PaperPortfolioService(Path(".")).run()

    assert all(item.status in {PASS, WARNING, FAIL} for item in run.result.governance)
    assert all(item.status in {PASS, WARNING, FAIL} for item in run.result.limits)
    assert all(0 <= item.score <= 100 for item in run.result.governance)
    assert all(0 <= item.score <= 100 for item in run.result.limits)
    assert 0 <= run.result.exposure["exposure_score"] <= 100
    assert 0 <= run.result.drawdown["drawdown_score"] <= 100


def test_paper_portfolio_dashboard_and_api_are_arabic() -> None:
    PaperPortfolioService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/paper-portfolio")
    api = client.get("/api/paper-portfolio")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "إدارة المحفظة الورقية" in page.text
    assert "المحفظة الورقية" in page.text
    assert "الأداء الورقي" in page.text
    assert "الحوكمة" in page.text
    assert "Paper Portfolio" not in page.text
    assert api.json()["summary"]["paper_only"] is True
    assert api.json()["summary"]["research_only"] is True
