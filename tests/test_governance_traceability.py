import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.governance_traceability.diagnostics import GovernanceTraceabilityDiagnostics
from app.governance_traceability.schemas import (
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.governance_traceability.service import GovernanceTraceabilityService


def test_governance_traceability_source_loading_handles_missing_optional_files(
    tmp_path: Path,
) -> None:
    sources = GovernanceTraceabilityService(tmp_path).load_sources()

    assert "sources" in sources
    assert "missing_sources" in sources
    assert sources["traceability_only"] is True


def test_governance_traceability_generation_is_traceability_only(
    tmp_path: Path,
) -> None:
    run = GovernanceTraceabilityService(tmp_path).run_full_governance_traceability()

    assert run.payloads["control_mappings"]["items"]
    assert run.payloads["control_matrix"]["items"]
    assert run.payloads["evidence_matrix"]["items"]
    assert run.payloads["readiness_mapping"]["items"]
    assert run.payloads["risk_mapping"]["items"]
    assert run.payloads["incident_mapping"]["items"]
    assert run.payloads["release_mapping"]["items"]
    assert run.payloads["monitoring_mapping"]["items"]
    assert run.payloads["policy_mapping"]["items"]
    assert run.payloads["coverage_summary"]["overall_traceability_score"] > 0
    assert run.summary["traceability_only"] is True
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
    assert run.summary["no_real_operational_control"] is True


def test_governance_traceability_outputs_and_readiness_states(
    tmp_path: Path,
) -> None:
    run = GovernanceTraceabilityService(tmp_path).run_full_governance_traceability()
    payload = json.dumps({"summary": run.summary}, ensure_ascii=False)

    assert run.summary["readiness_state"] in {
        "Not Ready",
        "Traceability Incomplete",
        "Ready For Governance Review",
    }
    assert not any(state in payload for state in FORBIDDEN_READINESS_STATES)
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_governance_traceability_diagnostics_detect_unsafe_wording(
    tmp_path: Path,
) -> None:
    diagnostics = GovernanceTraceabilityDiagnostics().evaluate(
        tmp_path,
        {"coverage_summary": {"readiness_state": FORBIDDEN_READINESS_STATES[0]}},
    )
    codes = {item["code"] for item in diagnostics}

    assert "missing-control_mappings" in codes
    assert "missing-source_inventory" in codes
    assert "forbidden-readiness-state" in codes


def test_governance_traceability_recommendations_are_arabic(tmp_path: Path) -> None:
    recommendations = GovernanceTraceabilityService(tmp_path).generate_recommendations()

    assert len(recommendations) >= 10
    assert any("التتبع" in item for item in recommendations)


def test_governance_traceability_dashboard_and_api_routes() -> None:
    GovernanceTraceabilityService(Path(".")).run_full_governance_traceability()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/governance-traceability",
        "/api/governance-traceability",
        "/api/governance-traceability/mappings",
        "/api/governance-traceability/control-matrix",
        "/api/governance-traceability/evidence-matrix",
        "/api/governance-traceability/readiness",
        "/api/governance-traceability/risks",
        "/api/governance-traceability/incidents",
        "/api/governance-traceability/releases",
        "/api/governance-traceability/monitoring",
        "/api/governance-traceability/policies",
        "/api/governance-traceability/coverage",
        "/api/governance-traceability/diagnostics",
        "/api/governance-traceability/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "تتبع الحوكمة وربط الضوابط" in responses["/governance-traceability"].text
    assert responses["/api/governance-traceability"].json()["summary"]["traceability_only"] is True


def test_governance_traceability_module_has_no_forbidden_capability() -> None:
    module_dir = Path("app/governance_traceability")
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()

    assert not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS)
