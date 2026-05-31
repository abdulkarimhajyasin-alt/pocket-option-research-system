from pathlib import Path

from fastapi.testclient import TestClient

from app.broker_readiness.capabilities import CapabilityAssessmentEngine
from app.broker_readiness.diagnostics import BrokerReadinessDiagnostics
from app.broker_readiness.diagnostics import BrokerReadinessRecommendationEngine
from app.broker_readiness.models import ObservationCapability
from app.broker_readiness.readiness import BrokerObservationReadinessEngine
from app.broker_readiness.restrictions import SafetyRestrictionEngine
from app.broker_readiness.service import BrokerReadinessService
from app.broker_readiness.validation import ObservationValidationEngine
from app.dashboard.routes import create_dashboard_app


def test_broker_readiness_engines_are_bounded_and_passive():
    capability = ObservationCapability(
        market_visibility=72,
        asset_visibility=70,
        payout_visibility=64,
        session_visibility=76,
        candle_visibility=82,
        signal_visibility=68,
    )
    assessment = CapabilityAssessmentEngine().assess(capability)
    restrictions = SafetyRestrictionEngine().evaluate()
    validation = ObservationValidationEngine().validate(assessment, restrictions)
    readiness = BrokerObservationReadinessEngine().evaluate(
        assessment,
        validation,
        restrictions,
    )
    diagnostics = BrokerReadinessDiagnostics().evaluate(
        readiness,
        validation,
        restrictions,
    )
    recommendations = BrokerReadinessRecommendationEngine().generate(diagnostics)

    assert 0 <= capability.score <= 100
    assert 0 <= assessment.score <= 100
    assert 0 <= validation.score <= 100
    assert 0 <= readiness.score <= 100
    assert restrictions.status == "PASS"
    assert all(item.status == "PASS" for item in restrictions.checks)
    assert isinstance(recommendations, tuple)


def test_broker_readiness_service_generates_outputs():
    run = BrokerReadinessService(Path(".")).run()
    assert run.result.readiness.state
    assert run.result.metadata["observation_only"] is True
    assert run.result.metadata["not_execution"] is True
    assert run.result.metadata["not_order_placement"] is True
    assert run.result.metadata["not_account_action"] is True
    assert run.result.metadata["not_automation"] is True
    assert run.result.metadata["not_broker_control"] is True
    assert run.result.to_dict()["observation_only"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_broker_readiness_dashboard_and_api_are_arabic():
    BrokerReadinessService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/broker-readiness")
    api = client.get("/api/broker-readiness")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "جاهزية المراقبة الخارجية" in page.text
    assert "درجة الجاهزية" in page.text
    assert "توزيع الجاهزية" in page.text
    assert "Broker Readiness" not in page.text
    assert api.json()["summary"]["observation_only"] is True
