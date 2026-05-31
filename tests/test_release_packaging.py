import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.release_packaging.schemas import (
    FORBIDDEN_RELEASE_STATUSES,
    RELEASE_ID,
    SAFE_RELEASE_STATUSES,
)
from app.release_packaging.service import ReleasePackagingService


def test_release_manifest_and_status_are_safe(tmp_path: Path) -> None:
    run = ReleasePackagingService(tmp_path).run_full_release_packaging()

    assert run.manifest["release_id"] == RELEASE_ID
    assert run.manifest["release_status"] in SAFE_RELEASE_STATUSES
    assert not any(
        state in json.dumps(run.manifest, ensure_ascii=False)
        for state in FORBIDDEN_RELEASE_STATUSES
    )
    assert all(run.manifest["safety_boundary"].values())
    assert run.project_status["recommended_next_decision"] in {
        "Freeze as Research Platform v1.0",
        "Run targeted cleanup before release",
        "Continue only with a separate post-research roadmap",
    }


def test_release_audit_notes_diagnostics_and_recommendations(tmp_path: Path) -> None:
    service = ReleasePackagingService(tmp_path)
    audit = service.run_repository_audit()
    run = service.run_full_release_packaging()

    assert audit["missing_expected"]["modules"]
    assert run.release_notes["research_only"] is True
    assert "release_title" in run.release_notes
    assert run.diagnostics
    assert all("ت" in item or "ة" in item for item in run.recommendations)
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_release_packaging_dashboard_and_api_routes() -> None:
    ReleasePackagingService(Path(".")).run_full_release_packaging()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/release-packaging",
        "/api/release-packaging",
        "/api/release-packaging/manifest",
        "/api/release-packaging/status",
        "/api/release-packaging/notes",
        "/api/release-packaging/diagnostics",
        "/api/release-packaging/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "تغليف الإصدار النهائي" in responses["/release-packaging"].text
    assert responses["/api/release-packaging/manifest"].json()["release_id"] == RELEASE_ID
    assert responses["/api/release-packaging/status"].json()["research_only"] is True
