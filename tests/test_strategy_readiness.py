from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.strategy_readiness.gates import DeploymentGateEngine
from app.strategy_readiness.readiness import StrategyReadinessEngine
from app.strategy_readiness.recommendations import RecommendationEngine
from app.strategy_readiness.service import StrategyReadinessService
from app.strategy_readiness.validation import GateRequirementsEngine
from app.strategy_readiness.validation import ResearchStabilityEngine


def _inputs() -> dict:
    return {
        "signal_summary": {"average_confidence": 72, "total_signals": 120},
        "performance_summary": {
            "total_signals": 110,
            "consistency_score": 68,
            "confidence_accuracy_score": 74,
        },
        "opportunity_summary": {"average_score": 70},
        "timeframe_summary": {"average_alignment": 65},
        "confluence_summary": {"average_confluence": 62},
        "lifecycle_summary": {"average_quality": 66, "total_lifecycles": 100},
    }


def test_readiness_and_gate_engines_are_bounded():
    inputs = _inputs()
    stability = ResearchStabilityEngine().evaluate(inputs)
    readiness = StrategyReadinessEngine().evaluate(inputs, stability.score)
    gates = DeploymentGateEngine().evaluate(readiness.components, stability.score)
    requirements = GateRequirementsEngine().evaluate(inputs, readiness.score)
    assert 0 <= readiness.score <= 100
    assert len(gates) == 7
    assert {gate.status for gate in gates}.issubset({"PASS", "WARNING", "FAIL"})
    assert requirements.passed is True


def test_recommendations_are_arabic_and_deterministic():
    inputs = _inputs()
    stability = ResearchStabilityEngine().evaluate(inputs)
    readiness = StrategyReadinessEngine().evaluate(inputs, stability.score)
    gates = DeploymentGateEngine().evaluate(readiness.components, stability.score)
    from app.strategy_readiness.diagnostics import StrategyDiagnosticsEngine

    diagnostics = StrategyDiagnosticsEngine().evaluate(readiness.components, gates)
    recommendations = RecommendationEngine().generate(
        readiness.components,
        diagnostics,
    )
    assert recommendations
    assert all(item.title for item in recommendations)


def test_strategy_readiness_service_generates_outputs():
    run = StrategyReadinessService(Path(".")).run()
    assert run.result.readiness.score >= 0
    assert run.result.metadata["not_execution"] is True
    assert run.result.to_dict()["not_deployment_approval"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_strategy_readiness_dashboard_and_api_are_arabic():
    StrategyReadinessService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/strategy-readiness")
    api = client.get("/api/strategy-readiness")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "جاهزية الاستراتيجية" in page.text
    assert "تقييم الجاهزية الاستراتيجية" in page.text
    assert "Strategy Readiness" not in page.text
