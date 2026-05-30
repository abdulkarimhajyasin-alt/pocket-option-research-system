from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.research_certification.certification import ResearchCertificationEngine
from app.research_certification.consistency import ResearchConsistencyEngine
from app.research_certification.requirements import CertificationRequirementsEngine
from app.research_certification.robustness import ResearchRobustnessEngine
from app.research_certification.service import ResearchCertificationService
from app.research_certification.stability import ResearchStabilityEngine


def _inputs() -> dict[str, float]:
    return {
        "sample_size": 80,
        "research_quality": 72,
        "signal_quality": 70,
        "signal_consistency": 68,
        "opportunity_quality": 66,
        "confluence_quality": 69,
        "lifecycle_quality": 71,
        "readiness_score": 73,
        "readiness_stability": 67,
        "benchmark_score": 74,
        "benchmark_stability": 70,
        "pattern_quality": 68,
        "pattern_reliability": 72,
        "pattern_stability": 65,
        "pattern_adaptation": 70,
        "regime_score": 64,
        "regime_stability": 62,
        "confidence_accuracy": 69,
    }


def test_certification_engines_are_bounded():
    inputs = _inputs()
    robustness = ResearchRobustnessEngine().evaluate(inputs)
    consistency = ResearchConsistencyEngine().evaluate(inputs)
    stability = ResearchStabilityEngine().evaluate(inputs)
    requirements = CertificationRequirementsEngine().evaluate(
        inputs,
        robustness.score,
        consistency.score,
        stability.score,
    )
    certification = ResearchCertificationEngine().evaluate(
        inputs,
        robustness,
        consistency,
        stability,
    )
    assert 0 <= certification.score <= 100
    assert 0 <= robustness.score <= 100
    assert 0 <= consistency.score <= 100
    assert 0 <= stability.score <= 100
    assert requirements.checks


def test_research_certification_service_generates_outputs():
    run = ResearchCertificationService(Path(".")).run()
    assert run.result.certification.state
    assert run.result.metadata["not_execution"] is True
    assert run.result.to_dict()["not_deployment_approval"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_research_certification_dashboard_and_api_are_arabic():
    ResearchCertificationService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/research-certification")
    api = client.get("/api/research-certification")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "محرك الاعتماد البحثي" in page.text
    assert "شهادة الجاهزية البحثية" in page.text
    assert "Research Certification" not in page.text
