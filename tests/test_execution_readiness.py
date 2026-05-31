from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.execution_readiness.gates import ExecutionGateEngine
from app.execution_readiness.models import FAIL, PASS, WARNING
from app.execution_readiness.readiness import ExecutionReadinessEngine
from app.execution_readiness.service import ExecutionReadinessService


def test_execution_readiness_engines_are_bounded() -> None:
    run = ExecutionReadinessService(Path(".")).run()
    readiness = ExecutionReadinessEngine().evaluate(run.result.candidates, {})
    gates = ExecutionGateEngine().evaluate(run.result.candidates, readiness, {})

    assert len(run.result.candidates) >= 5
    assert 0 <= readiness.score <= 100
    assert all(gate.state in {PASS, WARNING, FAIL} for gate in gates)
    assert all(0 <= gate.score <= 100 for gate in gates)


def test_execution_readiness_service_generates_outputs() -> None:
    run = ExecutionReadinessService(Path(".")).run()

    assert run.result.metadata["research_only"] is True
    assert run.result.metadata["readiness_only"] is True
    assert run.result.metadata["not_execution"] is True
    assert run.result.metadata["not_order_placement"] is True
    assert run.result.metadata["not_account_login"] is True
    assert run.result.metadata["not_broker_authentication"] is True
    assert run.result.metadata["not_credential_handling"] is True
    assert run.result.metadata["not_browser_automation"] is True
    assert run.result.metadata["not_broker_control"] is True
    assert run.result.to_dict()["readiness_only"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_execution_readiness_dashboard_and_api_are_arabic() -> None:
    ExecutionReadinessService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/execution-readiness")
    api = client.get("/api/execution-readiness")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "إطار جاهزية التنفيذ" in page.text
    assert "جاهزية التنفيذ" in page.text
    assert "توزيع الجاهزية" in page.text
    assert "نتائج البوابات" in page.text
    assert "Execution Readiness" not in page.text
    assert api.json()["summary"]["research_only"] is True
    assert api.json()["summary"]["readiness_only"] is True
    assert api.json()["summary"]["not_execution"] is True
