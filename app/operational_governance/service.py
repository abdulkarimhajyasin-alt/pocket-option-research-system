"""Service layer for operational governance framework."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.operational_governance.approval_workflows import ApprovalWorkflowBuilder
from app.operational_governance.audit_controls import AuditControlBuilder
from app.operational_governance.authority_model import OperationalAuthorityModelBuilder
from app.operational_governance.change_management import ChangeManagementBuilder
from app.operational_governance.control_evidence import ControlEvidenceBuilder
from app.operational_governance.decision_matrix import DecisionMatrixBuilder
from app.operational_governance.diagnostics import OperationalGovernanceDiagnostics
from app.operational_governance.incident_escalation import IncidentEscalationBuilder
from app.operational_governance.kill_switch_governance import KillSwitchGovernanceBuilder
from app.operational_governance.operator_responsibility import (
    OperatorResponsibilityBuilder,
)
from app.operational_governance.policy_registry import PolicyRegistryBuilder
from app.operational_governance.readiness_gates import GovernanceReadinessGateEngine
from app.operational_governance.recommendations import (
    OperationalGovernanceRecommendationBuilder,
)
from app.operational_governance.release_governance import ReleaseGovernanceBuilder
from app.operational_governance.reports import OperationalGovernanceReportWriter
from app.operational_governance.review_boards import ReviewBoardBuilder
from app.operational_governance.schemas import GOVERNANCE_ONLY_FLAGS
from app.operational_governance.storage import OperationalGovernanceStorage


@dataclass(frozen=True)
class OperationalGovernanceRunResult:
    """Result of one governance generation cycle."""

    payloads: dict[str, Any]
    diagnostics: list[dict[str, str]]
    recommendations: list[str]
    summary: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class OperationalGovernanceEngine:
    """Build all governance-only framework documents."""

    def __init__(self) -> None:
        self.builders = {
            "authority_model": OperationalAuthorityModelBuilder(),
            "approval_workflows": ApprovalWorkflowBuilder(),
            "change_management": ChangeManagementBuilder(),
            "release_governance": ReleaseGovernanceBuilder(),
            "incident_escalation": IncidentEscalationBuilder(),
            "kill_switch_governance": KillSwitchGovernanceBuilder(),
            "audit_controls": AuditControlBuilder(),
            "operator_responsibility": OperatorResponsibilityBuilder(),
            "review_boards": ReviewBoardBuilder(),
            "decision_matrix": DecisionMatrixBuilder(),
            "control_evidence": ControlEvidenceBuilder(),
            "policy_registry": PolicyRegistryBuilder(),
        }
        self.readiness = GovernanceReadinessGateEngine()

    def build_all(self) -> dict[str, Any]:
        payloads = {key: builder.build().to_dict() for key, builder in self.builders.items()}
        payloads["readiness_gates"] = self.readiness.build()
        return payloads

    def build_summary(
        self,
        payloads: dict[str, Any],
        diagnostics: list[dict[str, str]],
        recommendations: list[str],
    ) -> dict[str, Any]:
        return {
            "governance_status": "Governance Incomplete",
            "governance_domain_count": len(payloads) - 1,
            "authority_role_count": len(payloads["authority_model"].get("items", [])),
            "approval_workflow_count": len(payloads["approval_workflows"].get("items", [])),
            "change_control_count": len(payloads["change_management"].get("items", [])),
            "release_governance_status": "Governance only",
            "incident_escalation_status": "Governance only",
            "kill_switch_governance_status": "Governance only",
            "audit_control_count": len(payloads["audit_controls"].get("items", [])),
            "review_board_count": len(payloads["review_boards"].get("items", [])),
            "decision_rule_count": len(payloads["decision_matrix"].get("items", [])),
            "policy_count": len(payloads["policy_registry"].get("items", [])),
            "readiness_state": payloads["readiness_gates"]["readiness_state"],
            "diagnostic_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            **GOVERNANCE_ONLY_FLAGS,
        }


class OperationalGovernanceService:
    """Generate local governance-only framework artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.engine = OperationalGovernanceEngine()
        self.diagnostics_builder = OperationalGovernanceDiagnostics()
        self.recommendation_builder = OperationalGovernanceRecommendationBuilder()
        self.storage = OperationalGovernanceStorage(
            self.project_root / "storage" / "operational_governance"
        )
        self.reports = OperationalGovernanceReportWriter(
            self.project_root / "reports" / "operational_governance"
        )

    def build_authority_model(self) -> dict[str, Any]:
        return self.engine.builders["authority_model"].build().to_dict()

    def build_approval_workflows(self) -> dict[str, Any]:
        return self.engine.builders["approval_workflows"].build().to_dict()

    def build_change_management(self) -> dict[str, Any]:
        return self.engine.builders["change_management"].build().to_dict()

    def build_release_governance(self) -> dict[str, Any]:
        return self.engine.builders["release_governance"].build().to_dict()

    def build_incident_escalation(self) -> dict[str, Any]:
        return self.engine.builders["incident_escalation"].build().to_dict()

    def build_kill_switch_governance(self) -> dict[str, Any]:
        return self.engine.builders["kill_switch_governance"].build().to_dict()

    def build_audit_controls(self) -> dict[str, Any]:
        return self.engine.builders["audit_controls"].build().to_dict()

    def build_operator_responsibility(self) -> dict[str, Any]:
        return self.engine.builders["operator_responsibility"].build().to_dict()

    def build_review_boards(self) -> dict[str, Any]:
        return self.engine.builders["review_boards"].build().to_dict()

    def build_decision_matrix(self) -> dict[str, Any]:
        return self.engine.builders["decision_matrix"].build().to_dict()

    def build_control_evidence(self) -> dict[str, Any]:
        return self.engine.builders["control_evidence"].build().to_dict()

    def build_policy_registry(self) -> dict[str, Any]:
        return self.engine.builders["policy_registry"].build().to_dict()

    def build_readiness_gates(self) -> dict[str, Any]:
        return self.engine.readiness.build()

    def build_summary(self) -> dict[str, Any]:
        payloads = self.engine.build_all()
        diagnostics = self.diagnostics_builder.evaluate(self.project_root, payloads)
        recommendations = self.generate_recommendations()
        return self.engine.build_summary(payloads, diagnostics, recommendations)

    def generate_diagnostics(self) -> list[dict[str, str]]:
        return self.diagnostics_builder.evaluate(self.project_root, self.engine.build_all())

    def generate_recommendations(self) -> list[str]:
        return self.recommendation_builder.build()

    def run_full_operational_governance(self) -> OperationalGovernanceRunResult:
        payloads = self.engine.build_all()
        diagnostics = self.diagnostics_builder.evaluate(self.project_root, payloads)
        recommendations = self.generate_recommendations()
        summary = self.engine.build_summary(payloads, diagnostics, recommendations)
        payloads = {
            **payloads,
            "diagnostics": diagnostics,
            "recommendations": recommendations,
            "summary": summary,
        }
        storage_paths = self.storage.save(payloads)
        report_paths = self.reports.export(payloads)
        return OperationalGovernanceRunResult(
            payloads=payloads,
            diagnostics=diagnostics,
            recommendations=recommendations,
            summary=summary,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )

    def get_summary(self) -> dict[str, Any]:
        payload = self._read_json(
            "reports",
            "operational_governance",
            "operational_governance_summary.json",
        )
        if isinstance(payload, dict) and payload:
            return payload
        return self.run_full_operational_governance().summary

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
