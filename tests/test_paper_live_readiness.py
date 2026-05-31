from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.paper_live_readiness.models import FAIL, PASS, WARNING
from app.paper_live_readiness.service import PaperToLiveReadinessService


def test_paper_live_readiness_service_generates_outputs() -> None:
    run = PaperToLiveReadinessService(Path(".")).run()

    assert 0 <= run.result.readiness.overall_score <= 100
    assert 0 <= run.result.safety["safety_score"] <= 100
    assert 0 <= run.result.maturity["maturity_score"] <= 100
    assert 0 <= run.result.stability["stability_score"] <= 100
    assert run.result.metadata["readiness_only"] is True
    assert run.result.metadata["paper_only"] is True
    assert run.result.metadata["research_only"] is True
    assert run.result.metadata["not_live_trading"] is True
    assert run.result.metadata["not_broker_access"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_paper_live_readiness_gates_and_safety_are_bounded() -> None:
    run = PaperToLiveReadinessService(Path(".")).run()

    assert all(item.status in {PASS, WARNING, FAIL} for item in run.result.gates)
    assert all(0 <= item.score <= 100 for item in run.result.gates)
    assert run.result.safety["status"] == PASS
    assert run.result.safety["no_execution"] is True
    assert run.result.safety["no_live_trading"] is True
    assert run.result.safety["no_broker_access"] is True
    assert run.result.safety["no_order_placement"] is True


def test_paper_live_readiness_dashboard_and_api_are_arabic() -> None:
    PaperToLiveReadinessService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/paper-live-readiness")
    api = client.get("/api/paper-live-readiness")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "بوابة الجاهزية للمرحلة التالية" in page.text
    assert "جاهزية المرحلة التالية" in page.text
    assert "توزيع الجاهزية" in page.text
    assert "نتائج البوابات" in page.text
    assert "Paper-to-Live" not in page.text
    assert api.json()["summary"]["readiness_only"] is True
    assert api.json()["summary"]["paper_only"] is True
    assert api.json()["summary"]["research_only"] is True
