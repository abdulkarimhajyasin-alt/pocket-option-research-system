"""Service layer for control assurance and review readiness."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.control_assurance.assurance_engine import ControlAssuranceEngine
from app.control_assurance.audit_readiness import AuditReadinessAssessmentEngine
from app.control_assurance.diagnostics import ControlAssuranceDiagnostics
from app.control_assurance.evidence_assessment import EvidenceSufficiencyAssessmentEngine
from app.control_assurance.gate_assessment import GateMaturityAssessmentEngine
from app.control_assurance.owner_assessment import OwnerClarityAssessmentEngine
from app.control_assurance.policy_assessment import PolicyCompletenessAssessmentEngine
from app.control_assurance.recommendations import ControlAssuranceRecommendationBuilder
from app.control_assurance.reports import ControlAssuranceReportWriter
from app.control_assurance.review_readiness import GovernanceReviewReadinessEngine
from app.control_assurance.schemas import ASSURANCE_ONLY_FLAGS
from app.control_assurance.scoring import ControlAssuranceScoringEngine
from app.control_assurance.source_loader import ControlAssuranceSourceLoader
from app.control_assurance.storage import ControlAssuranceStorage
from app.control_assurance.weakness_assessment import WeaknessAssessmentEngine


@dataclass(frozen=True)
class ControlAssuranceRunResult:
    """Result of one assurance generation cycle."""

    payloads: dict[str, Any]
    diagnostics: list[dict[str, str]]
    recommendations: list[str]
    summary: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ControlAssuranceService:
    """Generate local assurance-only review readiness artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.loader = ControlAssuranceSourceLoader(self.project_root)
        self.control_engine = ControlAssuranceEngine()
        self.evidence_engine = EvidenceSufficiencyAssessmentEngine()
        self.owner_engine = OwnerClarityAssessmentEngine()
        self.policy_engine = PolicyCompletenessAssessmentEngine()
        self.gate_engine = GateMaturityAssessmentEngine()
        self.weakness_engine = WeaknessAssessmentEngine()
        self.audit_engine = AuditReadinessAssessmentEngine()
        self.readiness_engine = GovernanceReviewReadinessEngine()
        self.scoring_engine = ControlAssuranceScoringEngine()
        self.diagnostics_builder = ControlAssuranceDiagnostics()
        self.recommendation_builder = ControlAssuranceRecommendationBuilder()
        self.storage = ControlAssuranceStorage(self.project_root / "storage" / "control_assurance")
        self.reports = ControlAssuranceReportWriter(
            self.project_root / "reports" / "control_assurance"
        )

    def load_sources(self) -> dict[str, Any]:
        return self.loader.load()

    def assess_control_quality(self) -> dict[str, Any]:
        return self.control_engine.assess(self.load_sources())

    def assess_evidence_sufficiency(self) -> dict[str, Any]:
        return self.evidence_engine.assess()

    def assess_owner_clarity(self) -> dict[str, Any]:
        return self.owner_engine.assess()

    def assess_policy_completeness(self) -> dict[str, Any]:
        return self.policy_engine.assess()

    def assess_gate_maturity(self) -> dict[str, Any]:
        return self.gate_engine.assess()

    def assess_weaknesses(self) -> dict[str, Any]:
        return self.weakness_engine.assess()

    def assess_audit_readiness(self) -> dict[str, Any]:
        payloads = self._build_assessment_payloads()
        scorecard = self.scoring_engine.build(payloads)
        return self.audit_engine.assess(scorecard)

    def assess_governance_review_readiness(self) -> dict[str, Any]:
        payloads = self._build_assessment_payloads()
        scorecard = self.scoring_engine.build(payloads)
        return self.readiness_engine.assess(payloads, scorecard)

    def build_scorecard(self) -> dict[str, Any]:
        return self.scoring_engine.build(self._build_assessment_payloads())

    def generate_diagnostics(self) -> list[dict[str, str]]:
        return self.diagnostics_builder.evaluate(
            self.project_root,
            self._build_payloads(include_summary=False),
        )

    def generate_recommendations(self) -> list[str]:
        return self.recommendation_builder.build()

    def run_full_control_assurance(self) -> ControlAssuranceRunResult:
        payloads = self._build_payloads(include_summary=False)
        diagnostics = self.diagnostics_builder.evaluate(self.project_root, payloads)
        recommendations = self.generate_recommendations()
        summary = self._summary(payloads, diagnostics, recommendations)
        payloads = {
            **payloads,
            "diagnostics": diagnostics,
            "recommendations": recommendations,
            "summary": summary,
        }
        storage_paths = self.storage.save(payloads)
        report_paths = self.reports.export(payloads)
        return ControlAssuranceRunResult(
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
            "control_assurance",
            "control_assurance_summary.json",
        )
        if isinstance(payload, dict) and payload:
            return payload
        return self.run_full_control_assurance().summary

    def _build_assessment_payloads(self) -> dict[str, Any]:
        return {
            "source_inventory": self.load_sources(),
            "control_quality": self.assess_control_quality(),
            "evidence_sufficiency": self.assess_evidence_sufficiency(),
            "owner_clarity": self.assess_owner_clarity(),
            "policy_completeness": self.assess_policy_completeness(),
            "gate_maturity": self.assess_gate_maturity(),
            "weakness_assessment": self.assess_weaknesses(),
        }

    def _build_payloads(self, include_summary: bool = True) -> dict[str, Any]:
        payloads = self._build_assessment_payloads()
        payloads["scorecard"] = self.scoring_engine.build(payloads)
        payloads["audit_readiness"] = self.audit_engine.assess(payloads["scorecard"])
        payloads["review_readiness"] = self.readiness_engine.assess(
            payloads,
            payloads["scorecard"],
        )
        if include_summary:
            diagnostics = self.diagnostics_builder.evaluate(self.project_root, payloads)
            recommendations = self.generate_recommendations()
            payloads["summary"] = self._summary(payloads, diagnostics, recommendations)
        return payloads

    def _summary(
        self,
        payloads: dict[str, Any],
        diagnostics: list[dict[str, str]],
        recommendations: list[str],
    ) -> dict[str, Any]:
        scorecard = payloads["scorecard"]
        review = payloads["review_readiness"]
        return {
            "assurance_status": scorecard["score_status"],
            "review_readiness_state": review["review_readiness_state"],
            "overall_assurance_score": scorecard["overall_assurance_score"],
            "control_quality_score": scorecard["control_quality_score"],
            "evidence_sufficiency_score": scorecard["evidence_sufficiency_score"],
            "owner_clarity_score": scorecard["owner_clarity_score"],
            "policy_completeness_score": scorecard["policy_completeness_score"],
            "gate_maturity_score": scorecard["gate_maturity_score"],
            "audit_readiness_score": scorecard["audit_readiness_score"],
            "governance_review_readiness_score": scorecard["governance_review_readiness_score"],
            "weakness_count": len(payloads["weakness_assessment"].get("items", [])),
            "blocker_count": review["blocker_count"],
            "diagnostic_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            **ASSURANCE_ONLY_FLAGS,
        }

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
