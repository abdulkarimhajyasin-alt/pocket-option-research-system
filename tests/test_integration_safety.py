from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.integration_safety.models import ALLOWED_CAPABILITIES, FORBIDDEN_CAPABILITIES
from app.integration_safety.service import IntegrationSafetyService


def test_integration_safety_service_generates_outputs() -> None:
    run = IntegrationSafetyService(Path(".")).run()

    assert 0 <= run.result.policy.safety_score <= 100
    assert 0 <= run.result.policy.compliance_score <= 100
    assert tuple(run.result.policy.allowed_capabilities) == ALLOWED_CAPABILITIES
    assert tuple(run.result.policy.forbidden_capabilities) == FORBIDDEN_CAPABILITIES
    assert run.result.metadata["safety_boundary_only"] is True
    assert run.result.metadata["readiness_only"] is True
    assert run.result.metadata["research_only"] is True
    assert run.result.metadata["not_broker_access"] is True
    assert run.result.metadata["not_browser_automation"] is True
    assert run.result.metadata["not_external_execution_adapter"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_integration_safety_allowed_and_forbidden_capabilities() -> None:
    run = IntegrationSafetyService(Path(".")).run()

    assert run.result.permissions["permission_score"] == 100.0
    assert run.result.restrictions["restriction_score"] == 100.0
    assert run.result.restrictions["violations"] == []
    assert "broker connection" in run.result.policy.forbidden_capabilities
    assert "local report reading" in run.result.policy.allowed_capabilities
    assert run.result.compliance["no_execution_compliance"] is True
    assert run.result.compliance["no_broker_compliance"] is True
    assert run.result.compliance["no_browser_automation_compliance"] is True


def test_integration_safety_dashboard_and_api_are_arabic() -> None:
    IntegrationSafetyService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/integration-safety")
    api = client.get("/api/integration-safety")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "حدود أمان التكامل الخارجي" in page.text
    assert "أمان التكامل" in page.text
    assert "توزيع السلامة" in page.text
    assert "القدرات المحظورة" in page.text
    assert "External Integration" not in page.text
    assert api.json()["summary"]["safety_boundary_only"] is True
    assert api.json()["summary"]["readiness_only"] is True
    assert api.json()["summary"]["research_only"] is True
