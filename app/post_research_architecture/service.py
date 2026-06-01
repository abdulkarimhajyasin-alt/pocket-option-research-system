"""Service layer for post-research strategic architecture planning."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.post_research_architecture.boundaries import PostResearchBoundaryBuilder
from app.post_research_architecture.broker_blueprint import BrokerBlueprintBuilder
from app.post_research_architecture.diagnostics import PostResearchArchitectureDiagnostics
from app.post_research_architecture.execution_blueprint import ExecutionBlueprintBuilder
from app.post_research_architecture.gap_analysis import PostResearchGapAnalysisEngine
from app.post_research_architecture.governance_blueprint import GovernanceBlueprintBuilder
from app.post_research_architecture.monitoring_blueprint import MonitoringBlueprintBuilder
from app.post_research_architecture.recommendations import PostResearchRecommendationBuilder
from app.post_research_architecture.reports import PostResearchArchitectureReportWriter
from app.post_research_architecture.risk_blueprint import RiskBlueprintBuilder
from app.post_research_architecture.roadmap import PostResearchRoadmapBuilder
from app.post_research_architecture.schemas import (
    ARCHITECTURE_ONLY_FLAGS,
    CURRENT_PLATFORM_STATE,
    NEXT_PROGRAM_NAME,
)
from app.post_research_architecture.storage import PostResearchArchitectureStorage
from app.post_research_architecture.transition_plan import PostResearchTransitionPlanner


@dataclass(frozen=True)
class PostResearchArchitectureRunResult:
    """Result of one post-research architecture generation cycle."""

    roadmap: dict[str, Any]
    gap_analysis: dict[str, Any]
    execution_blueprint: dict[str, Any]
    broker_blueprint: dict[str, Any]
    risk_blueprint: dict[str, Any]
    monitoring_blueprint: dict[str, Any]
    governance_blueprint: dict[str, Any]
    transition_plan: dict[str, Any]
    diagnostics: list[dict[str, Any]]
    recommendations: list[str]
    summary: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class PostResearchArchitectureService:
    """Generate local architecture-only post-research planning artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.roadmap_builder = PostResearchRoadmapBuilder()
        self.gap_engine = PostResearchGapAnalysisEngine()
        self.execution_builder = ExecutionBlueprintBuilder()
        self.broker_builder = BrokerBlueprintBuilder()
        self.risk_builder = RiskBlueprintBuilder()
        self.monitoring_builder = MonitoringBlueprintBuilder()
        self.governance_builder = GovernanceBlueprintBuilder()
        self.transition_planner = PostResearchTransitionPlanner()
        self.boundary_builder = PostResearchBoundaryBuilder()
        self.diagnostics_builder = PostResearchArchitectureDiagnostics()
        self.recommendation_builder = PostResearchRecommendationBuilder()
        self.storage = PostResearchArchitectureStorage(
            self.project_root / "storage" / "post_research_architecture"
        )
        self.reports = PostResearchArchitectureReportWriter(
            self.project_root / "reports" / "post_research_architecture"
        )

    def build_roadmap(self) -> dict[str, Any]:
        return self.roadmap_builder.build().to_dict()

    def build_gap_analysis(self) -> dict[str, Any]:
        return self.gap_engine.build().to_dict()

    def build_execution_blueprint(self) -> dict[str, Any]:
        return self.execution_builder.build().to_dict()

    def build_broker_blueprint(self) -> dict[str, Any]:
        return self.broker_builder.build().to_dict()

    def build_risk_blueprint(self) -> dict[str, Any]:
        return self.risk_builder.build().to_dict()

    def build_monitoring_blueprint(self) -> dict[str, Any]:
        return self.monitoring_builder.build().to_dict()

    def build_governance_blueprint(self) -> dict[str, Any]:
        return self.governance_builder.build().to_dict()

    def build_transition_plan(self) -> dict[str, Any]:
        return self.transition_planner.build().to_dict()

    def generate_diagnostics(self) -> list[dict[str, Any]]:
        payloads = self._build_payloads()
        return self.diagnostics_builder.evaluate(
            self.project_root,
            payloads["roadmap"],
            payloads["gap_analysis"],
            self._blueprints(payloads),
            payloads["transition_plan"],
            payloads["summary"],
        )

    def generate_recommendations(self) -> list[str]:
        return self.recommendation_builder.build()

    def run_full_post_research_architecture(self) -> PostResearchArchitectureRunResult:
        payloads = self._build_payloads()
        diagnostics = self.diagnostics_builder.evaluate(
            self.project_root,
            payloads["roadmap"],
            payloads["gap_analysis"],
            self._blueprints(payloads),
            payloads["transition_plan"],
            payloads["summary"],
        )
        recommendations = self.generate_recommendations()
        payloads["diagnostics"] = diagnostics
        payloads["recommendations"] = recommendations
        payloads["summary"] = self._summary(payloads, diagnostics, recommendations)
        storage_paths = self.storage.save(payloads)
        report_paths = self.reports.export(payloads)
        return PostResearchArchitectureRunResult(
            roadmap=payloads["roadmap"],
            gap_analysis=payloads["gap_analysis"],
            execution_blueprint=payloads["execution_blueprint"],
            broker_blueprint=payloads["broker_blueprint"],
            risk_blueprint=payloads["risk_blueprint"],
            monitoring_blueprint=payloads["monitoring_blueprint"],
            governance_blueprint=payloads["governance_blueprint"],
            transition_plan=payloads["transition_plan"],
            diagnostics=diagnostics,
            recommendations=recommendations,
            summary=payloads["summary"],
            storage_paths=storage_paths,
            report_paths=report_paths,
        )

    def get_summary(self) -> dict[str, Any]:
        payload = self._read_json(
            "reports", "post_research_architecture", "post_research_summary.json"
        )
        if payload:
            return payload
        return self.run_full_post_research_architecture().summary

    def roadmap(self) -> dict[str, Any]:
        return self._read_or_build("roadmap.json", self.build_roadmap)

    def gaps(self) -> dict[str, Any]:
        return self._read_or_build("gap_analysis.json", self.build_gap_analysis)

    def blueprints(self) -> dict[str, Any]:
        return {
            "execution": self._read_or_build(
                "execution_blueprint.json",
                self.build_execution_blueprint,
            ),
            "broker": self._read_or_build("broker_blueprint.json", self.build_broker_blueprint),
            "risk": self._read_or_build("risk_blueprint.json", self.build_risk_blueprint),
            "monitoring": self._read_or_build(
                "monitoring_blueprint.json",
                self.build_monitoring_blueprint,
            ),
            "governance": self._read_or_build(
                "governance_blueprint.json",
                self.build_governance_blueprint,
            ),
        }

    def transition(self) -> dict[str, Any]:
        return self._read_or_build("transition_plan.json", self.build_transition_plan)

    def _build_payloads(self) -> dict[str, Any]:
        roadmap = self.build_roadmap()
        gaps = self.build_gap_analysis()
        payloads = {
            "roadmap": roadmap,
            "gap_analysis": gaps,
            "execution_blueprint": self.build_execution_blueprint(),
            "broker_blueprint": self.build_broker_blueprint(),
            "risk_blueprint": self.build_risk_blueprint(),
            "monitoring_blueprint": self.build_monitoring_blueprint(),
            "governance_blueprint": self.build_governance_blueprint(),
            "transition_plan": self.build_transition_plan(),
            "boundaries": self.boundary_builder.build().to_dict(),
            "diagnostics": [],
            "recommendations": [],
        }
        payloads["summary"] = self._summary(payloads, [], [])
        return payloads

    def _summary(
        self,
        payloads: dict[str, Any],
        diagnostics: list[dict[str, Any]],
        recommendations: list[str],
    ) -> dict[str, Any]:
        gaps = payloads.get("gap_analysis", {})
        technical_gaps = gaps.get("technical_gaps", []) if isinstance(gaps, dict) else []
        levels = [str(item.get("gap_level")) for item in technical_gaps if isinstance(item, dict)]
        return {
            "current_platform_state": CURRENT_PLATFORM_STATE,
            "recommended_future_program": NEXT_PROGRAM_NAME,
            "architecture_separation_decision": "Separate future program required",
            "gap_count": len(technical_gaps),
            "highest_gap_level": (
                "حرج" if "حرج" in levels else (levels[0] if levels else "غير متاح")
            ),
            "future_execution_status": "Blueprint only; not implemented",
            "future_broker_status": "Blueprint only; not implemented",
            "risk_status": "Future governance design required",
            "monitoring_status": "Future monitoring design required",
            "governance_status": "Human approval gates required",
            "warning_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            "first_safe_next_step": payloads.get("transition_plan", {}).get("first_safe_next_step"),
            "boundaries": payloads.get("boundaries", {}),
            **ARCHITECTURE_ONLY_FLAGS,
        }

    def _blueprints(self, payloads: dict[str, Any]) -> dict[str, dict[str, Any]]:
        return {
            "execution": payloads["execution_blueprint"],
            "broker": payloads["broker_blueprint"],
            "risk": payloads["risk_blueprint"],
            "monitoring": payloads["monitoring_blueprint"],
            "governance": payloads["governance_blueprint"],
        }

    def _read_or_build(self, filename: str, builder) -> dict[str, Any]:
        payload = self._read_json("storage", "post_research_architecture", filename)
        return payload if payload else builder()

    def _read_json(self, *parts: str) -> dict[str, Any]:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}
