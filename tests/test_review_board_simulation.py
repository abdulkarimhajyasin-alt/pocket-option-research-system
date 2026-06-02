import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.review_board_simulation.diagnostics import ReviewBoardSimulationDiagnostics
from app.review_board_simulation.schemas import (
    FORBIDDEN_DECISION_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.review_board_simulation.service import ReviewBoardSimulationService


def test_source_loading_handles_missing_optional_files(tmp_path: Path) -> None:
    sources = ReviewBoardSimulationService(tmp_path).load_sources()

    assert "sources" in sources
    assert "missing_sources" in sources
    assert sources["simulation_only"] is True
    assert sources["local_only"] is True


def test_full_review_board_simulation_is_safe(tmp_path: Path) -> None:
    run = ReviewBoardSimulationService(tmp_path).run_full_review_board_simulation()

    assert run.payloads["board_registry"]["boards"]
    assert run.payloads["board_simulation_results"]["items"]
    assert run.payloads["gate_dry_run_results"]["items"]
    assert run.payloads["evidence_review"]["items"]
    assert "items" in run.payloads["blocker_analysis"]
    assert run.payloads["decision_scores"]["overall_review_readiness_score"] >= 0
    assert "items" in run.payloads["findings"]
    assert run.payloads["readiness_summary"]["simulation_only"] is True
    assert run.summary["simulation_only"] is True
    assert run.summary["review_only"] is True
    assert run.summary["dry_run_only"] is True
    assert run.summary["governance_only"] is True
    assert run.summary["design_only"] is True
    assert run.summary["architecture_only"] is True
    assert run.summary["research_only"] is True
    assert run.summary["local_only"] is True
    assert run.summary["no_broker_access"] is True
    assert run.summary["no_execution_capability"] is True
    assert run.summary["no_trading_capability"] is True
    assert run.summary["no_authentication"] is True
    assert run.summary["no_credentials"] is True
    assert run.summary["no_browser_automation"] is True
    assert run.summary["no_money_handling"] is True


def test_forbidden_decision_states_never_appear(tmp_path: Path) -> None:
    run = ReviewBoardSimulationService(tmp_path).run_full_review_board_simulation()
    payload = json.dumps(run.payloads, ensure_ascii=False)

    assert not any(state in payload for state in FORBIDDEN_DECISION_STATES)


def test_diagnostics_detect_unsafe_wording(tmp_path: Path) -> None:
    diagnostics = ReviewBoardSimulationDiagnostics().evaluate(
        tmp_path,
        {"decision_scores": {"overall_review_readiness_score": 10}, "unsafe": "broker-ready"},
    )
    codes = {item["code"] for item in diagnostics}

    assert "missing-source_inventory" in codes
    assert "unsafe-wording" in codes


def test_recommendations_are_arabic(tmp_path: Path) -> None:
    recommendations = ReviewBoardSimulationService(tmp_path).generate_recommendations()

    assert len(recommendations) >= 10
    assert any("مراجعة" in item for item in recommendations)


def test_dashboard_and_api_routes() -> None:
    ReviewBoardSimulationService(Path(".")).run_full_review_board_simulation()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/review-board-simulation",
        "/api/review-board-simulation",
        "/api/review-board-simulation/boards",
        "/api/review-board-simulation/decisions",
        "/api/review-board-simulation/gates",
        "/api/review-board-simulation/evidence",
        "/api/review-board-simulation/blockers",
        "/api/review-board-simulation/scores",
        "/api/review-board-simulation/findings",
        "/api/review-board-simulation/readiness",
        "/api/review-board-simulation/diagnostics",
        "/api/review-board-simulation/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "محاكاة مجالس المراجعة" in responses["/review-board-simulation"].text
    assert responses["/api/review-board-simulation"].json()["summary"]["simulation_only"] is True


def test_generated_json_files_are_valid(tmp_path: Path) -> None:
    run = ReviewBoardSimulationService(tmp_path).run_full_review_board_simulation()

    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_module_has_no_forbidden_capability() -> None:
    module_dir = Path("app/review_board_simulation")
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()

    assert not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS)
