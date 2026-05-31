from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.research_api.schemas import SNAPSHOT_KEYS
from app.research_api.service import UnifiedResearchAPIService


def test_research_api_snapshot_is_stable_and_research_only() -> None:
    service = UnifiedResearchAPIService(Path("."))
    first = service.snapshot().to_dict()
    second = service.snapshot().to_dict()

    assert first == second
    assert tuple(first.keys()) == SNAPSHOT_KEYS
    assert first["metadata"]["research_only"] is True
    assert first["metadata"]["not_execution"] is True
    assert first["metadata"]["not_broker_access"] is True
    assert first["metadata"]["not_browser_automation"] is True
    assert first["metadata"]["not_authentication"] is True
    assert first["metadata"]["not_real_money"] is True


def test_research_api_handles_missing_reports(tmp_path: Path) -> None:
    run = UnifiedResearchAPIService(tmp_path).run()
    snapshot = run.snapshot.to_dict()

    assert snapshot["diagnostics"]["data"]["summary"]["missing_source_count"] > 0
    assert snapshot["signals"]["available"] is True
    assert snapshot["metadata"]["stable_json_schema"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_research_api_dashboard_routes_return_safe_data() -> None:
    UnifiedResearchAPIService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/research-api",
        "/api/research",
        "/api/research/signals",
        "/api/research/opportunities",
        "/api/research/paper",
        "/api/research/readiness",
        "/api/research/knowledge-graph",
        "/api/research/diagnostics",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "واجهة البحث الموحدة" in responses["/research-api"].text
    assert responses["/api/research"].json()["research_only"] is True
    assert responses["/api/research/signals"].json()["metadata"]["research_only"] is True
    assert responses["/api/research/paper"].json()["metadata"]["research_only"] is True
    assert responses["/api/research/diagnostics"].json()["metadata"]["research_only"] is True
