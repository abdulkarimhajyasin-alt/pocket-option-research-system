import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.trading_architecture_program.schemas import FORBIDDEN_SOURCE_TERMS
from app.trading_architecture_program.service import TradingArchitectureProgramService


def test_trading_architecture_program_is_architecture_only(tmp_path: Path) -> None:
    run = TradingArchitectureProgramService(tmp_path).run_full_program_foundation()

    assert run.summary["architecture_only"] is True
    assert run.summary["no_execution_capability"] is True
    assert run.summary["no_broker_capability"] is True
    assert run.summary["no_trading_capability"] is True
    assert run.summary["no_external_connectivity"] is True
    assert len(run.domains) == 8
    assert len(run.gates) == 7
    assert len(run.workstreams) == 8
    assert all(gate["may_approve_live_trading"] is False for gate in run.gates)


def test_trading_architecture_program_outputs_exist(tmp_path: Path) -> None:
    run = TradingArchitectureProgramService(tmp_path).run_full_program_foundation()

    assert run.registry["program_name"] == "Trading System Architecture Program"
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_trading_architecture_program_dashboard_and_api_routes() -> None:
    TradingArchitectureProgramService(Path(".")).run_full_program_foundation()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/trading-architecture-program",
        "/api/trading-architecture-program",
        "/api/trading-architecture-program/gates",
        "/api/trading-architecture-program/workstreams",
        "/api/trading-architecture-program/domains",
        "/api/trading-architecture-program/diagnostics",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "برنامج هندسة نظام التداول المستقبلي" in responses["/trading-architecture-program"].text
    assert (
        responses["/api/trading-architecture-program"].json()["summary"]["architecture_only"]
        is True
    )


def test_trading_architecture_program_has_no_forbidden_capability() -> None:
    module_dir = Path("app/trading_architecture_program")
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()

    assert not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS)
