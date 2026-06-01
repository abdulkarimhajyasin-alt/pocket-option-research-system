"""Service layer for governance traceability mapping."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.governance_traceability.control_matrix import GovernanceControlMatrixEngine
from app.governance_traceability.coverage import GovernanceTraceabilityCoverageEngine
from app.governance_traceability.diagnostics import GovernanceTraceabilityDiagnostics
from app.governance_traceability.evidence_matrix import EvidenceMatrixBuilder
from app.governance_traceability.incident_mapping import IncidentMappingBuilder
from app.governance_traceability.mapping_engine import GovernanceTraceabilityMappingEngine
from app.governance_traceability.monitoring_mapping import MonitoringMappingBuilder
from app.governance_traceability.policy_mapping import PolicyMappingBuilder
from app.governance_traceability.readiness_mapping import ReadinessMappingBuilder
from app.governance_traceability.recommendations import (
    GovernanceTraceabilityRecommendationBuilder,
)
from app.governance_traceability.release_mapping import ReleaseMappingBuilder
from app.governance_traceability.reports import GovernanceTraceabilityReportWriter
from app.governance_traceability.risk_mapping import RiskMappingBuilder
from app.governance_traceability.schemas import TRACEABILITY_ONLY_FLAGS
from app.governance_traceability.source_loader import GovernanceTraceabilitySourceLoader
from app.governance_traceability.storage import GovernanceTraceabilityStorage


@dataclass(frozen=True)
class GovernanceTraceabilityRunResult:
    """Result of one traceability generation cycle."""

    payloads: dict[str, Any]
    diagnostics: list[dict[str, str]]
    recommendations: list[str]
    summary: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class GovernanceTraceabilityService:
    """Generate local traceability-only governance mappings."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.loader = GovernanceTraceabilitySourceLoader(self.project_root)
        self.mapping_engine = GovernanceTraceabilityMappingEngine()
        self.control_matrix_engine = GovernanceControlMatrixEngine()
        self.evidence_builder = EvidenceMatrixBuilder()
        self.readiness_builder = ReadinessMappingBuilder()
        self.risk_builder = RiskMappingBuilder()
        self.incident_builder = IncidentMappingBuilder()
        self.release_builder = ReleaseMappingBuilder()
        self.monitoring_builder = MonitoringMappingBuilder()
        self.policy_builder = PolicyMappingBuilder()
        self.coverage_engine = GovernanceTraceabilityCoverageEngine()
        self.diagnostics_builder = GovernanceTraceabilityDiagnostics()
        self.recommendation_builder = GovernanceTraceabilityRecommendationBuilder()
        self.storage = GovernanceTraceabilityStorage(
            self.project_root / "storage" / "governance_traceability"
        )
        self.reports = GovernanceTraceabilityReportWriter(
            self.project_root / "reports" / "governance_traceability"
        )

    def load_sources(self) -> dict[str, Any]:
        return self.loader.load()

    def build_control_mappings(self) -> dict[str, Any]:
        return self.mapping_engine.build(self.load_sources())

    def build_control_matrix(self) -> dict[str, Any]:
        return self.control_matrix_engine.build(self.build_control_mappings())

    def build_evidence_matrix(self) -> dict[str, Any]:
        return self.evidence_builder.build(self.build_control_mappings())

    def build_readiness_mapping(self) -> dict[str, Any]:
        return self.readiness_builder.build()

    def build_risk_mapping(self) -> dict[str, Any]:
        return self.risk_builder.build()

    def build_incident_mapping(self) -> dict[str, Any]:
        return self.incident_builder.build()

    def build_release_mapping(self) -> dict[str, Any]:
        return self.release_builder.build()

    def build_monitoring_mapping(self) -> dict[str, Any]:
        return self.monitoring_builder.build()

    def build_policy_mapping(self) -> dict[str, Any]:
        return self.policy_builder.build()

    def build_coverage_summary(self) -> dict[str, Any]:
        return self.coverage_engine.build(self._build_mapping_payloads())

    def generate_diagnostics(self) -> list[dict[str, str]]:
        payloads = self._build_payloads(include_summary=False)
        return self.diagnostics_builder.evaluate(self.project_root, payloads)

    def generate_recommendations(self) -> list[str]:
        return self.recommendation_builder.build()

    def run_full_governance_traceability(self) -> GovernanceTraceabilityRunResult:
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
        return GovernanceTraceabilityRunResult(
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
            "governance_traceability",
            "governance_traceability_summary.json",
        )
        if isinstance(payload, dict) and payload:
            return payload
        return self.run_full_governance_traceability().summary

    def _build_mapping_payloads(self) -> dict[str, Any]:
        sources = self.load_sources()
        control_mappings = self.mapping_engine.build(sources)
        return {
            "source_inventory": sources,
            "control_mappings": control_mappings,
            "control_matrix": self.control_matrix_engine.build(control_mappings),
            "evidence_matrix": self.evidence_builder.build(control_mappings),
            "readiness_mapping": self.readiness_builder.build(),
            "risk_mapping": self.risk_builder.build(),
            "incident_mapping": self.incident_builder.build(),
            "release_mapping": self.release_builder.build(),
            "monitoring_mapping": self.monitoring_builder.build(),
            "policy_mapping": self.policy_builder.build(),
        }

    def _build_payloads(self, include_summary: bool = True) -> dict[str, Any]:
        payloads = self._build_mapping_payloads()
        payloads["coverage_summary"] = self.coverage_engine.build(payloads)
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
        coverage = payloads["coverage_summary"]
        return {
            "traceability_status": "Traceability Incomplete",
            "readiness_state": coverage["readiness_state"],
            "mapping_count": len(payloads["control_mappings"].get("items", [])),
            "strong_mapping_count": coverage["strong_mappings"],
            "weak_mapping_count": coverage["weak_mappings"],
            "missing_mapping_count": coverage["unmapped_design_areas"],
            "uncovered_control_count": coverage["missing_controls"],
            "control_coverage_score": coverage["control_coverage_score"],
            "evidence_coverage_score": coverage["evidence_coverage_score"],
            "readiness_traceability_score": coverage["readiness_traceability_score"],
            "policy_coverage_score": coverage["policy_coverage_score"],
            "overall_traceability_score": coverage["overall_traceability_score"],
            "diagnostic_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            **TRACEABILITY_ONLY_FLAGS,
        }

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
