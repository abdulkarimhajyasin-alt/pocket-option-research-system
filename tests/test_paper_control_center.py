from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.paper_control_center.models import FAIL, PASS, WARNING
from app.paper_control_center.service import PaperControlCenterService


def test_paper_control_center_service_generates_outputs() -> None:
    run = PaperControlCenterService(Path(".")).run()

    assert 0 <= run.result.control.overall_score <= 100
    assert 0 <= run.result.health["health_score"] <= 100
    assert 0 <= run.result.monitoring["monitoring_score"] <= 100
    assert run.result.metadata["paper_only"] is True
    assert run.result.metadata["research_only"] is True
    assert run.result.metadata["recommendation_only"] is True
    assert run.result.metadata["not_real_execution"] is True
    assert run.result.metadata["not_broker_access"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_paper_control_center_governance_is_bounded() -> None:
    run = PaperControlCenterService(Path(".")).run()

    assert all(item.status in {PASS, WARNING, FAIL} for item in run.result.governance)
    assert all(0 <= item.score <= 100 for item in run.result.governance)
    assert run.result.decision["research_recommendation_only"] is True
    assert run.result.decision["paper_only"] is True


def test_paper_control_center_dashboard_and_api_are_arabic() -> None:
    PaperControlCenterService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/paper-control")
    api = client.get("/api/paper-control")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "مركز التحكم بالتداول الورقي" in page.text
    assert "مركز التحكم الورقي" in page.text
    assert "الصحة العامة" in page.text
    assert "القرار الحالي" in page.text
    assert "Paper Control" not in page.text
    assert api.json()["summary"]["paper_only"] is True
    assert api.json()["summary"]["research_only"] is True
