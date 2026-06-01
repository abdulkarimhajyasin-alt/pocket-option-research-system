import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.operational_governance.diagnostics import OperationalGovernanceDiagnostics
from app.operational_governance.schemas import (
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)
from app.operational_governance.service import OperationalGovernanceService


def test_operational_governance_generation_is_governance_only(tmp_path: Path) -> None:
    run = OperationalGovernanceService(tmp_path).run_full_operational_governance()

    assert run.payloads["authority_model"]["items"]
    assert run.payloads["approval_workflows"]["items"]
    assert run.payloads["change_management"]["items"]
    assert run.payloads["release_governance"]["items"]
    assert run.payloads["incident_escalation"]["items"]
    assert run.payloads["kill_switch_governance"]["items"]
    assert run.payloads["audit_controls"]["items"]
    assert run.payloads["operator_responsibility"]["items"]
    assert run.payloads["review_boards"]["items"]
    assert run.payloads["decision_matrix"]["items"]
    assert run.payloads["control_evidence"]["items"]
    assert run.payloads["policy_registry"]["items"]
    assert run.payloads["readiness_gates"]["gates"]
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


def test_operational_governance_outputs_and_readiness_states(
    tmp_path: Path,
) -> None:
    run = OperationalGovernanceService(tmp_path).run_full_operational_governance()
    payload = json.dumps(
        {"summary": run.summary, "gates": run.payloads["readiness_gates"]},
        ensure_ascii=False,
    )

    assert run.summary["readiness_state"] in {
        "Not Ready",
        "Governance Incomplete",
        "Ready For Governance Review",
    }
    assert not any(state in payload for state in FORBIDDEN_READINESS_STATES)
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_operational_governance_diagnostics_detect_unsafe_wording(
    tmp_path: Path,
) -> None:
    diagnostics = OperationalGovernanceDiagnostics().evaluate(
        tmp_path,
        {"readiness_gates": {"readiness_state": FORBIDDEN_READINESS_STATES[0]}},
    )
    codes = {item["code"] for item in diagnostics}

    assert "missing-authority_model" in codes
    assert "missing-approval_workflows" in codes
    assert "forbidden-readiness-state" in codes


def test_operational_governance_recommendations_are_arabic(tmp_path: Path) -> None:
    recommendations = OperationalGovernanceService(tmp_path).generate_recommendations()

    assert len(recommendations) >= 10
    assert any("الحوكمة" in item for item in recommendations)


def test_operational_governance_dashboard_and_api_routes() -> None:
    OperationalGovernanceService(Path(".")).run_full_operational_governance()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/operational-governance",
        "/api/operational-governance",
        "/api/operational-governance/authority",
        "/api/operational-governance/approval-workflows",
        "/api/operational-governance/change-management",
        "/api/operational-governance/release-governance",
        "/api/operational-governance/incidents",
        "/api/operational-governance/kill-switch",
        "/api/operational-governance/audit-controls",
        "/api/operational-governance/operators",
        "/api/operational-governance/review-boards",
        "/api/operational-governance/decision-matrix",
        "/api/operational-governance/control-evidence",
        "/api/operational-governance/policies",
        "/api/operational-governance/readiness-gates",
        "/api/operational-governance/diagnostics",
        "/api/operational-governance/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "إطار الحوكمة والتحكم التشغيلي" in responses["/operational-governance"].text
    assert responses["/api/operational-governance"].json()["summary"]["governance_only"] is True


def test_operational_governance_module_has_no_forbidden_capability() -> None:
    module_dir = Path("app/operational_governance")
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()

    assert not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS)
