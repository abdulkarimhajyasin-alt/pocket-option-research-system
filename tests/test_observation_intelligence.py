from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.observation_intelligence.aggregator import ObservationAggregator
from app.observation_intelligence.intelligence import ObservationIntelligenceEngine
from app.observation_intelligence.normalizer import ObservationNormalizer
from app.observation_intelligence.service import ObservationIntelligenceService
from app.observation_intelligence.validation import ObservationConfidenceEngine
from app.observation_intelligence.validation import ObservationQualityEngine
from app.observation_intelligence.validation import ObservationValidationEngine


def test_observation_intelligence_engines_are_bounded():
    observations, normalization = ObservationNormalizer(Path(".")).normalize()
    aggregation = ObservationAggregator().aggregate(observations)
    validation = ObservationValidationEngine().validate(observations, aggregation)
    confidence = ObservationConfidenceEngine().evaluate(observations, aggregation)
    quality = ObservationQualityEngine().evaluate(observations, aggregation, validation)
    intelligence = ObservationIntelligenceEngine().evaluate(
        aggregation,
        validation,
        confidence,
        quality,
    )

    assert len(observations) >= 4
    assert 0 <= normalization.score <= 100
    assert 0 <= aggregation.score <= 100
    assert 0 <= validation.score <= 100
    assert 0 <= confidence.score <= 100
    assert 0 <= quality.score <= 100
    assert 0 <= intelligence.score <= 100


def test_observation_intelligence_service_generates_outputs():
    run = ObservationIntelligenceService(Path(".")).run()
    assert run.result.intelligence.state
    assert run.result.metadata["observation_only"] is True
    assert run.result.metadata["not_execution"] is True
    assert run.result.metadata["not_order_placement"] is True
    assert run.result.metadata["not_account_login"] is True
    assert run.result.metadata["not_broker_authentication"] is True
    assert run.result.metadata["not_credential_handling"] is True
    assert run.result.metadata["not_browser_automation"] is True
    assert run.result.metadata["not_broker_control"] is True
    assert run.result.to_dict()["observation_only"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_observation_intelligence_dashboard_and_api_are_arabic():
    ObservationIntelligenceService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/observation-intelligence")
    api = client.get("/api/observation-intelligence")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "مركز ذكاء المراقبة" in page.text
    assert "توزيع المصادر" in page.text
    assert "تضارب البيانات" in page.text
    assert "Observation Intelligence" not in page.text
    assert api.json()["summary"]["observation_only"] is True
