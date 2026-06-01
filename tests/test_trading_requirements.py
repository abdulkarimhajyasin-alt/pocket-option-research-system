import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.trading_requirements.diagnostics import TradingRequirementsDiagnostics
from app.trading_requirements.schemas import (
    FORBIDDEN_DECISION_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.trading_requirements.service import TradingRequirementsService


def test_trading_requirements_generation_is_requirements_only(tmp_path: Path) -> None:
    run = TradingRequirementsService(tmp_path).run_full_requirements_specification()

    assert run.functional["items"]
    assert run.non_functional["items"]
    assert run.safety["items"]
    assert run.risk["items"]
    assert run.compliance["items"]
    assert run.broker["items"]
    assert run.execution["items"]
    assert run.monitoring["items"]
    assert run.data["items"]
    assert run.go_no_go["criteria"]
    assert run.summary["requirements_only"] is True
    assert run.summary["architecture_only"] is True
    assert run.summary["research_only"] is True
    assert run.summary["local_only"] is True
    assert run.summary["no_broker_access"] is True
    assert run.summary["no_execution_capability"] is True
    assert run.summary["no_money_handling"] is True


def test_trading_requirements_outputs_and_decision_states(tmp_path: Path) -> None:
    run = TradingRequirementsService(tmp_path).run_full_requirements_specification()
    payload = json.dumps(
        {"summary": run.summary, "go_no_go": run.go_no_go},
        ensure_ascii=False,
    )

    assert run.go_no_go["decision_state"] in {
        "Not Ready",
        "Requirements Incomplete",
        "Ready For Architecture Review",
    }
    assert not any(state in payload for state in FORBIDDEN_DECISION_STATES)
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_trading_requirements_diagnostics_detect_unsafe_wording(tmp_path: Path) -> None:
    diagnostics = TradingRequirementsDiagnostics().evaluate(
        tmp_path,
        requirements={},
        constraints={},
        go_no_go={"decision_state": FORBIDDEN_DECISION_STATES[0]},
    )
    codes = {item["code"] for item in diagnostics}

    assert "missing-requirement-category" in codes
    assert "missing-constraint-category" in codes
    assert "forbidden-decision-state" in codes


def test_trading_requirements_recommendations_are_arabic(tmp_path: Path) -> None:
    recommendations = TradingRequirementsService(tmp_path).generate_recommendations()

    assert len(recommendations) >= 10
    assert any("المتطلبات" in item for item in recommendations)


def test_trading_requirements_dashboard_and_api_routes() -> None:
    TradingRequirementsService(Path(".")).run_full_requirements_specification()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/trading-requirements",
        "/api/trading-requirements",
        "/api/trading-requirements/functional",
        "/api/trading-requirements/non-functional",
        "/api/trading-requirements/safety",
        "/api/trading-requirements/risk",
        "/api/trading-requirements/compliance",
        "/api/trading-requirements/broker",
        "/api/trading-requirements/execution",
        "/api/trading-requirements/monitoring",
        "/api/trading-requirements/data",
        "/api/trading-requirements/go-no-go",
        "/api/trading-requirements/diagnostics",
        "/api/trading-requirements/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "مواصفات متطلبات نظام التداول المستقبلي" in responses["/trading-requirements"].text
    assert responses["/api/trading-requirements"].json()["summary"]["requirements_only"] is True


def test_trading_requirements_module_has_no_forbidden_capability() -> None:
    module_dir = Path("app/trading_requirements")
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()

    assert not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS)
