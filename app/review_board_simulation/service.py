"""Service layer for review board simulation and decision gate dry runs."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.review_board_simulation.blocker_analysis import ReviewBlockerAnalysisEngine
from app.review_board_simulation.board_registry import ReviewBoardRegistry
from app.review_board_simulation.decision_scoring import ReviewDecisionScoringEngine
from app.review_board_simulation.diagnostics import ReviewBoardSimulationDiagnostics
from app.review_board_simulation.evidence_review import ReviewEvidenceEngine
from app.review_board_simulation.findings import ReviewSimulationFindingsBuilder
from app.review_board_simulation.gate_dry_run import DecisionGateDryRunEngine
from app.review_board_simulation.readiness import ReviewSimulationReadinessBuilder
from app.review_board_simulation.recommendations import ReviewSimulationRecommendationBuilder
from app.review_board_simulation.reports import ReviewBoardSimulationReportWriter
from app.review_board_simulation.review_simulator import ReviewBoardSimulationEngine
from app.review_board_simulation.schemas import SIMULATION_ONLY_FLAGS
from app.review_board_simulation.source_loader import ReviewBoardSimulationSourceLoader
from app.review_board_simulation.storage import ReviewBoardSimulationStorage


@dataclass(frozen=True)
class ReviewBoardSimulationRunResult:
    """Result of one simulation generation cycle."""

    payloads: dict[str, Any]
    diagnostics: list[dict[str, str]]
    recommendations: list[str]
    summary: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ReviewBoardSimulationService:
    """Generate local review-board simulation artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.loader = ReviewBoardSimulationSourceLoader(self.project_root)
        self.registry = ReviewBoardRegistry()
        self.evidence_engine = ReviewEvidenceEngine()
        self.review_engine = ReviewBoardSimulationEngine()
        self.gate_engine = DecisionGateDryRunEngine()
        self.blocker_engine = ReviewBlockerAnalysisEngine()
        self.scoring_engine = ReviewDecisionScoringEngine()
        self.findings_builder = ReviewSimulationFindingsBuilder()
        self.readiness_builder = ReviewSimulationReadinessBuilder()
        self.diagnostics_builder = ReviewBoardSimulationDiagnostics()
        self.recommendation_builder = ReviewSimulationRecommendationBuilder()
        self.storage = ReviewBoardSimulationStorage(
            self.project_root / "storage" / "review_board_simulation"
        )
        self.reports = ReviewBoardSimulationReportWriter(
            self.project_root / "reports" / "review_board_simulation"
        )

    def load_sources(self) -> dict[str, Any]:
        return self.loader.load()

    def build_board_registry(self) -> dict[str, Any]:
        return self.registry.build()

    def review_evidence(self) -> dict[str, Any]:
        return self.evidence_engine.review(self.load_sources(), self.build_board_registry())

    def simulate_board_reviews(self) -> dict[str, Any]:
        sources = self.load_sources()
        registry = self.build_board_registry()
        evidence = self.evidence_engine.review(sources, registry)
        return self.review_engine.simulate(sources, registry, evidence)

    def run_gate_dry_run(self) -> dict[str, Any]:
        evidence = self.review_evidence()
        boards = self.simulate_board_reviews()
        return self.gate_engine.run(boards, evidence)

    def analyze_blockers(self) -> dict[str, Any]:
        boards = self.simulate_board_reviews()
        gates = self.gate_engine.run(boards, self.review_evidence())
        return self.blocker_engine.analyze(boards, gates)

    def build_decision_scores(self) -> dict[str, Any]:
        evidence = self.review_evidence()
        boards = self.simulate_board_reviews()
        gates = self.gate_engine.run(boards, evidence)
        return self.scoring_engine.build(boards, gates, evidence)

    def build_findings(self) -> dict[str, Any]:
        boards = self.simulate_board_reviews()
        gates = self.gate_engine.run(boards, self.review_evidence())
        blockers = self.blocker_engine.analyze(boards, gates)
        return self.findings_builder.build(boards, gates, blockers)

    def build_readiness_summary(self) -> dict[str, Any]:
        payloads = self._build_payloads(include_summary=False)
        return self.readiness_builder.build(
            payloads["decision_scores"],
            payloads["board_simulation_results"],
            payloads["gate_dry_run_results"],
            payloads["blocker_analysis"],
        )

    def generate_diagnostics(self) -> list[dict[str, str]]:
        return self.diagnostics_builder.evaluate(
            self.project_root,
            self._build_payloads(include_summary=False),
        )

    def generate_recommendations(self) -> list[str]:
        return self.recommendation_builder.build()

    def run_full_review_board_simulation(self) -> ReviewBoardSimulationRunResult:
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
        return ReviewBoardSimulationRunResult(
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
            "review_board_simulation",
            "review_board_simulation_summary.json",
        )
        if isinstance(payload, dict) and payload:
            return payload
        return self.run_full_review_board_simulation().summary

    def _build_payloads(self, include_summary: bool = True) -> dict[str, Any]:
        sources = self.load_sources()
        registry = self.build_board_registry()
        evidence = self.evidence_engine.review(sources, registry)
        boards = self.review_engine.simulate(sources, registry, evidence)
        gates = self.gate_engine.run(boards, evidence)
        blockers = self.blocker_engine.analyze(boards, gates)
        scores = self.scoring_engine.build(boards, gates, evidence)
        findings = self.findings_builder.build(boards, gates, blockers)
        readiness = self.readiness_builder.build(scores, boards, gates, blockers)
        payloads = {
            "source_inventory": sources,
            "board_registry": registry,
            "board_simulation_results": boards,
            "gate_dry_run_results": gates,
            "evidence_review": evidence,
            "blocker_analysis": blockers,
            "decision_scores": scores,
            "findings": findings,
            "readiness_summary": readiness,
        }
        if include_summary:
            diagnostics = self.diagnostics_builder.evaluate(self.project_root, payloads)
            payloads["summary"] = self._summary(
                payloads,
                diagnostics,
                self.generate_recommendations(),
            )
        return payloads

    def _summary(
        self,
        payloads: dict[str, Any],
        diagnostics: list[dict[str, str]],
        recommendations: list[str],
    ) -> dict[str, Any]:
        scores = payloads["decision_scores"]
        readiness = payloads["readiness_summary"]
        return {
            "simulation_status": readiness["simulation_status"],
            "overall_review_readiness_score": scores["overall_review_readiness_score"],
            "board_readiness_score": round(
                sum(item["score"] for item in scores["board_scores"])
                / max(len(scores["board_scores"]), 1),
                2,
            ),
            "evidence_readiness_score": scores["evidence_readiness_score"],
            "gate_readiness_score": scores["gate_readiness_score"],
            "simulated_decision_count": readiness["simulated_decision_count"],
            "blocker_count": readiness["blocker_count"],
            "condition_count": readiness["condition_count"],
            "required_human_review_count": readiness["required_human_review_count"],
            "diagnostic_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            **SIMULATION_ONLY_FLAGS,
        }

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
