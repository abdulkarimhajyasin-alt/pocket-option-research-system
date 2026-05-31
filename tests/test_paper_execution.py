from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.paper_execution.models import RISK_FAIL, RISK_PASS, RISK_WARNING
from app.paper_execution.service import PaperExecutionService


def test_paper_execution_service_generates_outputs() -> None:
    run = PaperExecutionService(Path(".")).run()

    assert len(run.result.orders) >= 5
    assert len(run.result.lifecycle) >= len(run.result.orders)
    assert len(run.result.results) >= 1
    assert 0 <= run.result.score <= 100
    assert run.result.metadata["paper_only"] is True
    assert run.result.metadata["research_only"] is True
    assert run.result.metadata["not_real_execution"] is True
    assert run.result.metadata["not_real_order_placement"] is True
    assert run.result.metadata["not_broker_access"] is True
    assert run.result.metadata["not_browser_automation"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_paper_risk_gates_are_bounded() -> None:
    run = PaperExecutionService(Path(".")).run()

    assert all(
        item.status in {RISK_PASS, RISK_WARNING, RISK_FAIL}
        for item in run.result.risk_gates
    )
    assert all(0 <= item.score <= 100 for item in run.result.risk_gates)
    assert run.result.analytics["paper_only"] is True
    assert run.result.analytics["research_only"] is True


def test_paper_execution_dashboard_and_api_are_arabic() -> None:
    PaperExecutionService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/paper-execution")
    api = client.get("/api/paper-execution")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "محرك التنفيذ الورقي" in page.text
    assert "تنفيذ ورقي" in page.text
    assert "توزيع الأوامر الورقية" in page.text
    assert "المخاطر الورقية" in page.text
    assert "Paper Execution" not in page.text
    assert api.json()["summary"]["paper_only"] is True
    assert api.json()["summary"]["research_only"] is True
    assert api.json()["summary"]["not_real_execution"] is True
