from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.market_observation.aggregator import MarketObservationAggregator
from app.market_observation.normalizer import MarketObservationNormalizer
from app.market_observation.service import MarketObservationService
from app.market_observation.validation import MarketObservationValidationEngine


def test_market_observation_engines_are_bounded() -> None:
    observations = MarketObservationNormalizer(Path(".")).normalize()
    validation = MarketObservationValidationEngine().validate(observations)
    aggregate = MarketObservationAggregator().aggregate(observations, validation)

    assert len(observations) >= 5
    assert 0 <= validation.score <= 100
    assert 0 <= aggregate.score <= 100
    assert aggregate.state
    assert aggregate.source_distribution


def test_market_observation_service_generates_canonical_outputs() -> None:
    run = MarketObservationService(Path(".")).run()

    assert run.result.metadata["canonical_market_observation"] is True
    assert run.result.metadata["observation_only"] is True
    assert run.result.metadata["not_execution"] is True
    assert run.result.metadata["not_order_placement"] is True
    assert run.result.metadata["not_account_login"] is True
    assert run.result.metadata["not_broker_authentication"] is True
    assert run.result.metadata["not_credential_handling"] is True
    assert run.result.metadata["not_browser_automation"] is True
    assert run.result.metadata["not_broker_control"] is True
    assert run.result.to_dict()["canonical_market_observation"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_market_observation_dashboard_and_api_are_arabic() -> None:
    MarketObservationService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/market-observation")
    api = client.get("/api/market-observation")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "مصدر مراقبة السوق الموحد" in page.text
    assert "توزيع المصادر" in page.text
    assert "جودة المصادر" in page.text
    assert "Market Observation" not in page.text
    assert api.json()["summary"]["canonical_market_observation"] is True
