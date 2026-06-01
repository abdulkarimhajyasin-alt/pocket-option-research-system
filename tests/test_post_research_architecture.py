import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.post_research_architecture.diagnostics import (
    PostResearchArchitectureDiagnostics,
)
from app.post_research_architecture.schemas import (
    FORBIDDEN_SOURCE_TERMS,
    UNSAFE_STATE_PHRASES,
)
from app.post_research_architecture.service import PostResearchArchitectureService


def test_post_research_generation_is_architecture_only(tmp_path: Path) -> None:
    run = PostResearchArchitectureService(tmp_path).run_full_post_research_architecture()

    assert run.roadmap["current_platform_state"] == "Research Platform v1.0"
    assert run.gap_analysis["severity"] == "حرج"
    assert run.execution_blueprint["architecture_only"] is True
    assert run.execution_blueprint["not_implemented"] is True
    assert run.broker_blueprint["architecture_only"] is True
    assert run.broker_blueprint["not_implemented"] is True
    assert run.risk_blueprint["architecture_only"] is True
    assert run.monitoring_blueprint["architecture_only"] is True
    assert run.governance_blueprint["architecture_only"] is True
    assert run.transition_plan["recommended_next_program"] == (
        "Trading System Architecture Program"
    )
    assert run.summary["architecture_only"] is True
    assert run.summary["research_only"] is True
    assert run.summary["no_broker_access"] is True
    assert run.summary["no_order_placement"] is True
    assert run.summary["no_money_handling"] is True


def test_post_research_outputs_and_recommendations(tmp_path: Path) -> None:
    run = PostResearchArchitectureService(tmp_path).run_full_post_research_architecture()

    assert len(run.recommendations) >= 10
    assert all(isinstance(item, str) and item for item in run.recommendations)
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_post_research_diagnostics_detect_unsafe_wording(tmp_path: Path) -> None:
    diagnostics = PostResearchArchitectureDiagnostics().evaluate(
        tmp_path,
        roadmap={"state": UNSAFE_STATE_PHRASES[0]},
        gaps={},
        blueprints={},
        transition={},
        summary={"architecture_only": False},
    )

    codes = {item["code"] for item in diagnostics}
    assert "unsafe-state-wording" in codes
    assert "unclear-boundary" in codes


def test_post_research_dashboard_and_api_routes() -> None:
    PostResearchArchitectureService(Path(".")).run_full_post_research_architecture()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/post-research-architecture",
        "/api/post-research-architecture",
        "/api/post-research-architecture/roadmap",
        "/api/post-research-architecture/gaps",
        "/api/post-research-architecture/blueprints",
        "/api/post-research-architecture/transition",
        "/api/post-research-architecture/diagnostics",
        "/api/post-research-architecture/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert (
        "الهندسة الاستراتيجية لما بعد منصة البحث" in responses["/post-research-architecture"].text
    )
    assert responses["/api/post-research-architecture/roadmap"].json()["architecture_only"] is True
    assert responses["/api/post-research-architecture"].json()["summary"]["research_only"] is True


def test_post_research_module_has_no_forbidden_capability() -> None:
    module_dir = Path("app/post_research_architecture")
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()
    payload_text = json.dumps(
        PostResearchArchitectureService(Path(".")).run_full_post_research_architecture().summary
    )

    assert not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS)
    assert not any(state in payload_text for state in UNSAFE_STATE_PHRASES)
