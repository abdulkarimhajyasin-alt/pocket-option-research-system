import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.production_system_design.diagnostics import ProductionSystemDesignDiagnostics
from app.production_system_design.schemas import (
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.production_system_design.service import ProductionSystemDesignService


def test_production_system_design_generation_is_design_only(tmp_path: Path) -> None:
    run = ProductionSystemDesignService(tmp_path).run_full_production_design()

    assert run.payloads["topology"]["items"]
    assert run.payloads["service_boundaries"]["items"]
    assert run.payloads["runtime_architecture"]["items"]
    assert run.payloads["environment_strategy"]["items"]
    assert run.payloads["configuration_strategy"]["items"]
    assert run.payloads["secrets_strategy"]["items"]
    assert run.payloads["database_strategy"]["items"]
    assert run.payloads["event_queue_strategy"]["items"]
    assert run.payloads["logging_strategy"]["items"]
    assert run.payloads["monitoring_strategy"]["items"]
    assert run.payloads["alerting_strategy"]["items"]
    assert run.payloads["incident_response"]["items"]
    assert run.payloads["backup_recovery"]["items"]
    assert run.payloads["release_rollback"]["items"]
    assert run.payloads["readiness_gates"]["gates"]
    assert run.summary["design_only"] is True
    assert run.summary["architecture_only"] is True
    assert run.summary["research_only"] is True
    assert run.summary["local_only"] is True
    assert run.summary["no_broker_access"] is True
    assert run.summary["no_execution_capability"] is True
    assert run.summary["no_trading_capability"] is True
    assert run.summary["no_external_connectivity"] is True
    assert run.summary["no_real_production_deployment"] is True


def test_production_system_design_outputs_and_readiness_states(
    tmp_path: Path,
) -> None:
    run = ProductionSystemDesignService(tmp_path).run_full_production_design()
    payload = json.dumps(
        {"summary": run.summary, "gates": run.payloads["readiness_gates"]},
        ensure_ascii=False,
    )

    assert run.summary["readiness_state"] in {
        "Not Ready",
        "Design Incomplete",
        "Ready For Design Review",
    }
    assert not any(state in payload for state in FORBIDDEN_READINESS_STATES)
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_production_system_design_diagnostics_detect_unsafe_wording(
    tmp_path: Path,
) -> None:
    diagnostics = ProductionSystemDesignDiagnostics().evaluate(
        tmp_path,
        {"readiness_gates": {"readiness_state": FORBIDDEN_READINESS_STATES[0]}},
    )
    codes = {item["code"] for item in diagnostics}

    assert "missing-topology" in codes
    assert "missing-service_boundaries" in codes
    assert "forbidden-readiness-state" in codes


def test_production_system_design_recommendations_are_arabic(tmp_path: Path) -> None:
    recommendations = ProductionSystemDesignService(tmp_path).generate_recommendations()

    assert len(recommendations) >= 10
    assert any("التصميم" in item for item in recommendations)


def test_production_system_design_dashboard_and_api_routes() -> None:
    ProductionSystemDesignService(Path(".")).run_full_production_design()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/production-system-design",
        "/api/production-system-design",
        "/api/production-system-design/topology",
        "/api/production-system-design/service-boundaries",
        "/api/production-system-design/runtime",
        "/api/production-system-design/environments",
        "/api/production-system-design/configuration",
        "/api/production-system-design/secrets",
        "/api/production-system-design/database",
        "/api/production-system-design/events",
        "/api/production-system-design/logging",
        "/api/production-system-design/monitoring",
        "/api/production-system-design/alerting",
        "/api/production-system-design/incidents",
        "/api/production-system-design/backup-recovery",
        "/api/production-system-design/release-rollback",
        "/api/production-system-design/readiness-gates",
        "/api/production-system-design/diagnostics",
        "/api/production-system-design/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "مخطط تصميم النظام الإنتاجي المستقبلي" in responses["/production-system-design"].text
    assert responses["/api/production-system-design"].json()["summary"]["design_only"] is True


def test_production_system_design_module_has_no_forbidden_capability() -> None:
    module_dir = Path("app/production_system_design")
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()

    assert not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS)
