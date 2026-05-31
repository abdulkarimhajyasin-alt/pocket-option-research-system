from pathlib import Path

from fastapi.testclient import TestClient

from app.browser_observation.adapter import ReadOnlyObservationAdapter
from app.browser_observation.monitoring import ArtifactMonitoringEngine
from app.browser_observation.parser import ArtifactParserEngine
from app.browser_observation.safety import ReadOnlySafetyEngine
from app.browser_observation.service import BrowserObservationService
from app.browser_observation.validator import ArtifactValidationEngine
from app.browser_observation.visibility import VisibilityAssessmentEngine
from app.dashboard.routes import create_dashboard_app


def test_browser_observation_engines_are_bounded_and_read_only():
    adapter = ReadOnlyObservationAdapter(Path("."))
    artifacts = adapter.load_artifacts()
    parse = ArtifactParserEngine().parse(artifacts)
    validation = ArtifactValidationEngine().validate(artifacts)
    visibility = VisibilityAssessmentEngine().assess(artifacts, parse)
    monitoring = ArtifactMonitoringEngine().monitor(
        artifacts,
        validation,
        visibility,
    )
    safety = ReadOnlySafetyEngine().evaluate()
    adapter_score = adapter.score(
        parse.score,
        validation.score,
        visibility.score,
        monitoring.score,
        safety.score,
    )

    assert len(artifacts) >= 5
    assert 0 <= parse.score <= 100
    assert 0 <= validation.score <= 100
    assert 0 <= visibility.score <= 100
    assert 0 <= monitoring.score <= 100
    assert 0 <= adapter_score.score <= 100
    assert safety.status == "PASS"
    assert safety.no_login is True
    assert safety.no_authentication is True
    assert safety.no_browser_control is True
    assert safety.no_execution is True
    assert safety.no_order_apis is True
    assert safety.no_account_access is True
    assert safety.no_automation is True


def test_browser_observation_service_generates_outputs():
    run = BrowserObservationService(Path(".")).run()
    assert run.result.adapter.state
    assert run.result.metadata["read_only"] is True
    assert run.result.metadata["observation_only"] is True
    assert run.result.metadata["not_execution"] is True
    assert run.result.metadata["not_order_placement"] is True
    assert run.result.metadata["not_account_login"] is True
    assert run.result.metadata["not_broker_authentication"] is True
    assert run.result.metadata["not_credential_handling"] is True
    assert run.result.metadata["not_browser_automation"] is True
    assert run.result.metadata["not_broker_control"] is True
    assert run.result.to_dict()["read_only"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_browser_observation_dashboard_and_api_are_arabic():
    BrowserObservationService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/browser-observation")
    api = client.get("/api/browser-observation")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "مراقبة المتصفح للقراءة فقط" in page.text
    assert "توزيع اللقطات" in page.text
    assert "توزيع السلامة" in page.text
    assert "Browser Observation" not in page.text
    assert api.json()["summary"]["read_only"] is True
