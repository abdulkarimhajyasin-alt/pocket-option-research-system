import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.control_assurance.diagnostics import ControlAssuranceDiagnostics
from app.control_assurance.schemas import (
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.control_assurance.service import ControlAssuranceService
from app.dashboard.routes import create_dashboard_app


def test_control_assurance_source_loading_handles_missing_optional_files(
    tmp_path: Path,
) -> None:
    sources = ControlAssuranceService(tmp_path).load_sources()

    assert "sources" in sources
    assert "missing_sources" in sources
    assert sources["assurance_only"] is True


def test_control_assurance_generation_is_assurance_only(tmp_path: Path) -> None:
    run = ControlAssuranceService(tmp_path).run_full_control_assurance()

    assert run.payloads["control_quality"]["items"]
    assert run.payloads["evidence_sufficiency"]["items"]
    assert run.payloads["owner_clarity"]["items"]
    assert run.payloads["policy_completeness"]["items"]
    assert run.payloads["gate_maturity"]["items"]
    assert run.payloads["weakness_assessment"]["items"]
    assert run.payloads["audit_readiness"]["audit_readiness_score"] > 0
    assert run.payloads["review_readiness"]["review_readiness_state"]
    assert run.payloads["scorecard"]["overall_assurance_score"] > 0
    assert run.summary["assurance_only"] is True
    assert run.summary["review_readiness_only"] is True
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


def test_control_assurance_outputs_and_review_states(tmp_path: Path) -> None:
    run = ControlAssuranceService(tmp_path).run_full_control_assurance()
    payload = json.dumps({"summary": run.summary}, ensure_ascii=False)

    assert run.summary["review_readiness_state"] in {
        "Not Ready",
        "Review Blocked",
        "Ready For Governance Review",
    }
    assert not any(state in payload for state in FORBIDDEN_READINESS_STATES)
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_control_assurance_diagnostics_detect_unsafe_wording(tmp_path: Path) -> None:
    diagnostics = ControlAssuranceDiagnostics().evaluate(
        tmp_path,
        {"scorecard": {"readiness_state": FORBIDDEN_READINESS_STATES[0]}},
    )
    codes = {item["code"] for item in diagnostics}

    assert "missing-control_quality" in codes
    assert "missing-source_inventory" in codes
    assert "forbidden-readiness-state" in codes


def test_control_assurance_recommendations_are_arabic(tmp_path: Path) -> None:
    recommendations = ControlAssuranceService(tmp_path).generate_recommendations()

    assert len(recommendations) >= 10
    assert any("التأكيد" in item for item in recommendations)


def test_control_assurance_dashboard_and_api_routes() -> None:
    ControlAssuranceService(Path(".")).run_full_control_assurance()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/control-assurance",
        "/api/control-assurance",
        "/api/control-assurance/control-quality",
        "/api/control-assurance/evidence",
        "/api/control-assurance/owners",
        "/api/control-assurance/policies",
        "/api/control-assurance/gates",
        "/api/control-assurance/weaknesses",
        "/api/control-assurance/audit-readiness",
        "/api/control-assurance/review-readiness",
        "/api/control-assurance/scorecard",
        "/api/control-assurance/diagnostics",
        "/api/control-assurance/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "تأكيد الضوابط وجاهزية المراجعة" in responses["/control-assurance"].text
    assert responses["/api/control-assurance"].json()["summary"]["assurance_only"] is True


def test_control_assurance_module_has_no_forbidden_capability() -> None:
    module_dir = Path("app/control_assurance")
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()

    assert not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS)
