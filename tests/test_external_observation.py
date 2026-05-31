from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.external_observation.isolation import IsolationEngine
from app.external_observation.monitoring import ObservationMonitoringEngine
from app.external_observation.sandbox import ExternalObservationSandbox
from app.external_observation.sandbox import ObservationHealthEngine
from app.external_observation.service import ExternalObservationService
from app.external_observation.sources import ObservationSourceRegistry
from app.external_observation.validation import SourceValidationEngine


def test_external_observation_engines_are_bounded_and_isolated():
    sources = ObservationSourceRegistry(Path(".")).discover()
    validation = SourceValidationEngine().validate(sources)
    isolation = IsolationEngine().evaluate()
    monitoring = ObservationMonitoringEngine().monitor(sources, validation.score)
    health = ObservationHealthEngine().evaluate(
        validation,
        monitoring,
        isolation,
        sources,
    )
    sandbox = ExternalObservationSandbox().score(
        validation,
        monitoring,
        isolation,
        health,
    )

    assert len(sources) >= 4
    assert 0 <= validation.score <= 100
    assert 0 <= monitoring.score <= 100
    assert 0 <= health.score <= 100
    assert 0 <= sandbox.score <= 100
    assert isolation.status == "PASS"
    assert isolation.no_broker_connectivity is True
    assert isolation.no_account_access is True
    assert isolation.no_execution_paths is True
    assert isolation.no_authentication_flows is True
    assert isolation.no_order_apis is True


def test_external_observation_service_generates_outputs():
    run = ExternalObservationService(Path(".")).run()
    assert run.result.sandbox.state
    assert run.result.metadata["observation_only"] is True
    assert run.result.metadata["not_execution"] is True
    assert run.result.metadata["not_order_placement"] is True
    assert run.result.metadata["not_account_login"] is True
    assert run.result.metadata["not_broker_authentication"] is True
    assert run.result.metadata["not_browser_automation"] is True
    assert run.result.metadata["not_broker_control"] is True
    assert run.result.to_dict()["observation_only"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_external_observation_dashboard_and_api_are_arabic():
    ExternalObservationService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/external-observation")
    api = client.get("/api/external-observation")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "بيئة المراقبة الخارجية" in page.text
    assert "توزيع المصادر" in page.text
    assert "توزيع العزل" in page.text
    assert "External Observation" not in page.text
    assert api.json()["summary"]["observation_only"] is True
