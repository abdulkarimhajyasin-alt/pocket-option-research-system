from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.platform_certification.scoring import PlatformCertificationScoringEngine
from app.platform_certification.schemas import FORBIDDEN_STATES
from app.platform_certification.service import PlatformCertificationService


def test_platform_certification_scoring_and_states() -> None:
    scoring = PlatformCertificationScoringEngine()

    assert scoring.score_domain(1, 2) == 50.0
    assert scoring.domain_status(95) == "ممتاز"
    assert scoring.certification_state(50, 0) == "Not Certified"
    assert scoring.certification_state(80, 0) == "Conditionally Certified"
    assert scoring.certification_state(90, 0) == "Certified For Advanced Research"
    assert scoring.certification_state(95, 1) == "Not Certified"


def test_platform_certification_outputs_are_safe(tmp_path: Path) -> None:
    run = PlatformCertificationService(tmp_path).run()
    payload = run.certification.to_dict()
    text = str(payload)

    assert payload["research_only"] is True
    assert payload["local_only"] is True
    assert all(payload["safety_boundary"].values())
    assert len(payload["domain_scores"]) == 10
    assert payload["diagnostics"]
    assert payload["recommendations"]
    assert not any(state in text for state in FORBIDDEN_STATES)
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_platform_certification_dashboard_and_api_routes() -> None:
    PlatformCertificationService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/platform-certification",
        "/api/platform-certification",
        "/api/platform-certification/summary",
        "/api/platform-certification/domains",
        "/api/platform-certification/diagnostics",
        "/api/platform-certification/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "الشهادة النهائية للمنصة البحثية" in responses["/platform-certification"].text
    assert responses["/api/platform-certification"].json()["research_only"] is True
    assert responses["/api/platform-certification/summary"].json()["research_only"] is True
