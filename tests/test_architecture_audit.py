from pathlib import Path

from fastapi.testclient import TestClient

from app.architecture_audit.service import ArchitectureAuditService
from app.dashboard.routes import create_dashboard_app


def test_architecture_audit_service_generates_outputs() -> None:
    run = ArchitectureAuditService(Path(".")).run()

    assert 0 <= run.result.certification.overall_score <= 100
    assert 0 <= run.result.certification.architecture_score <= 100
    assert 0 <= run.result.certification.consistency_score <= 100
    assert 0 <= run.result.certification.performance_score <= 100
    assert 0 <= run.result.certification.safety_score <= 100
    assert run.result.metadata["architecture_audit_only"] is True
    assert run.result.metadata["hardening_only"] is True
    assert run.result.metadata["research_only"] is True
    assert run.result.metadata["not_real_execution"] is True
    assert run.result.metadata["not_broker_access"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_architecture_audit_safety_and_consistency_are_bounded() -> None:
    run = ArchitectureAuditService(Path(".")).run()

    assert run.result.safety["no_execution_paths"] is True
    assert run.result.safety["no_broker_paths"] is True
    assert run.result.safety["no_login_auth_paths"] is True
    assert run.result.safety["no_automation_paths"] is True
    assert run.result.consistency["report_count"] >= 1
    assert run.result.consistency["storage_count"] >= 1


def test_architecture_audit_dashboard_and_api_are_arabic() -> None:
    ArchitectureAuditService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/architecture-audit")
    api = client.get("/api/architecture-audit")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "التدقيق النهائي للمنصة" in page.text
    assert "تدقيق المنصة" in page.text
    assert "درجة المعمارية" in page.text
    assert "حالة الاعتماد النهائي" in page.text
    assert "Architecture Audit" not in page.text
    assert api.json()["summary"]["architecture_audit_only"] is True
    assert api.json()["summary"]["hardening_only"] is True
    assert api.json()["summary"]["research_only"] is True
