"""Service layer for trading requirements specification."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.trading_requirements.broker_constraints import BrokerConstraintsBuilder
from app.trading_requirements.compliance_constraints import ComplianceConstraintsBuilder
from app.trading_requirements.data_constraints import DataConstraintsBuilder
from app.trading_requirements.diagnostics import TradingRequirementsDiagnostics
from app.trading_requirements.execution_constraints import ExecutionConstraintsBuilder
from app.trading_requirements.functional import FunctionalRequirementsBuilder
from app.trading_requirements.go_no_go import TradingConstraintEngine, TradingGoNoGoEngine
from app.trading_requirements.models import RequirementCoverageSummary
from app.trading_requirements.monitoring_constraints import MonitoringConstraintsBuilder
from app.trading_requirements.non_functional import NonFunctionalRequirementsBuilder
from app.trading_requirements.operational_constraints import OperationalConstraintsBuilder
from app.trading_requirements.recommendations import TradingRequirementsRecommendationBuilder
from app.trading_requirements.reports import TradingRequirementsReportWriter
from app.trading_requirements.risk_requirements import RiskRequirementsBuilder
from app.trading_requirements.safety_requirements import SafetyRequirementsBuilder
from app.trading_requirements.schemas import REQUIREMENTS_ONLY_FLAGS
from app.trading_requirements.storage import TradingRequirementsStorage


@dataclass(frozen=True)
class TradingRequirementsRunResult:
    """Result of one trading requirements generation cycle."""

    functional: dict[str, Any]
    non_functional: dict[str, Any]
    safety: dict[str, Any]
    risk: dict[str, Any]
    compliance: dict[str, Any]
    operational: dict[str, Any]
    broker: dict[str, Any]
    execution: dict[str, Any]
    monitoring: dict[str, Any]
    data: dict[str, Any]
    go_no_go: dict[str, Any]
    coverage: dict[str, Any]
    diagnostics: list[dict[str, str]]
    recommendations: list[str]
    summary: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class TradingRequirementsSpecificationEngine:
    """Build all requirements and constraints documents."""

    def __init__(self) -> None:
        self.functional = FunctionalRequirementsBuilder()
        self.non_functional = NonFunctionalRequirementsBuilder()
        self.safety = SafetyRequirementsBuilder()
        self.risk = RiskRequirementsBuilder()
        self.compliance = ComplianceConstraintsBuilder()
        self.operational = OperationalConstraintsBuilder()
        self.broker = BrokerConstraintsBuilder()
        self.execution = ExecutionConstraintsBuilder()
        self.monitoring = MonitoringConstraintsBuilder()
        self.data = DataConstraintsBuilder()
        self.go_no_go = TradingGoNoGoEngine()
        self.constraints = TradingConstraintEngine()

    def build_requirements(self) -> dict[str, dict[str, Any]]:
        return {
            "functional": self.functional.build().to_dict(),
            "non_functional": self.non_functional.build().to_dict(),
            "safety": self.safety.build().to_dict(),
            "risk": self.risk.build().to_dict(),
        }

    def build_constraints(self) -> dict[str, dict[str, Any]]:
        return {
            "compliance": self.compliance.build().to_dict(),
            "operational": self.operational.build().to_dict(),
            "broker": self.broker.build().to_dict(),
            "execution": self.execution.build().to_dict(),
            "monitoring": self.monitoring.build().to_dict(),
            "data": self.data.build().to_dict(),
        }

    def build_go_no_go(self) -> dict[str, Any]:
        criteria = self.go_no_go.build_criteria()
        return self.go_no_go.evaluate(criteria)

    def build_coverage_summary(
        self,
        requirements: dict[str, dict[str, Any]],
        constraints: dict[str, dict[str, Any]],
        go_no_go: dict[str, Any],
    ) -> RequirementCoverageSummary:
        requirement_count = sum(len(item.get("items", [])) for item in requirements.values())
        constraint_count = sum(len(item.get("items", [])) for item in constraints.values())
        return RequirementCoverageSummary(
            requirement_count=requirement_count,
            constraint_count=constraint_count,
            category_count=len(requirements) + len(constraints),
            highest_priority="مرتفع",
            go_no_go_state=str(go_no_go.get("decision_state", "Not Ready")),
            safety_requirement_count=len(requirements["safety"].get("items", [])),
            risk_requirement_count=len(requirements["risk"].get("items", [])),
            compliance_constraint_count=len(constraints["compliance"].get("items", [])),
            execution_constraint_count=len(constraints["execution"].get("items", [])),
            broker_constraint_count=len(constraints["broker"].get("items", [])),
        )


class TradingRequirementsService:
    """Generate local requirements-only planning artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.engine = TradingRequirementsSpecificationEngine()
        self.diagnostics_builder = TradingRequirementsDiagnostics()
        self.recommendation_builder = TradingRequirementsRecommendationBuilder()
        self.storage = TradingRequirementsStorage(
            self.project_root / "storage" / "trading_requirements"
        )
        self.reports = TradingRequirementsReportWriter(
            self.project_root / "reports" / "trading_requirements"
        )

    def build_functional_requirements(self) -> dict[str, Any]:
        return self.engine.functional.build().to_dict()

    def build_non_functional_requirements(self) -> dict[str, Any]:
        return self.engine.non_functional.build().to_dict()

    def build_safety_requirements(self) -> dict[str, Any]:
        return self.engine.safety.build().to_dict()

    def build_risk_requirements(self) -> dict[str, Any]:
        return self.engine.risk.build().to_dict()

    def build_compliance_constraints(self) -> dict[str, Any]:
        return self.engine.compliance.build().to_dict()

    def build_operational_constraints(self) -> dict[str, Any]:
        return self.engine.operational.build().to_dict()

    def build_broker_constraints(self) -> dict[str, Any]:
        return self.engine.broker.build().to_dict()

    def build_execution_constraints(self) -> dict[str, Any]:
        return self.engine.execution.build().to_dict()

    def build_monitoring_constraints(self) -> dict[str, Any]:
        return self.engine.monitoring.build().to_dict()

    def build_data_constraints(self) -> dict[str, Any]:
        return self.engine.data.build().to_dict()

    def build_go_no_go_criteria(self) -> dict[str, Any]:
        return self.engine.build_go_no_go()

    def build_coverage_summary(self) -> dict[str, Any]:
        requirements = self.engine.build_requirements()
        constraints = self.engine.build_constraints()
        go_no_go = self.engine.build_go_no_go()
        return self.engine.build_coverage_summary(
            requirements,
            constraints,
            go_no_go,
        ).to_dict()

    def generate_diagnostics(self) -> list[dict[str, str]]:
        requirements = self.engine.build_requirements()
        constraints = self.engine.build_constraints()
        go_no_go = self.engine.build_go_no_go()
        return self.diagnostics_builder.evaluate(
            self.project_root,
            requirements,
            constraints,
            go_no_go,
        )

    def generate_recommendations(self) -> list[str]:
        return self.recommendation_builder.build()

    def run_full_requirements_specification(self) -> TradingRequirementsRunResult:
        requirements = self.engine.build_requirements()
        constraints = self.engine.build_constraints()
        go_no_go = self.engine.build_go_no_go()
        coverage = self.engine.build_coverage_summary(
            requirements,
            constraints,
            go_no_go,
        ).to_dict()
        diagnostics = self.diagnostics_builder.evaluate(
            self.project_root,
            requirements,
            constraints,
            go_no_go,
        )
        recommendations = self.generate_recommendations()
        constraint_summary = self.engine.constraints.summarize(constraints)
        summary = {
            "requirements_status": "Requirements Incomplete",
            "requirement_count": coverage["requirement_count"],
            "constraint_count": coverage["constraint_count"],
            "highest_priority": coverage["highest_priority"],
            "go_no_go_state": go_no_go["decision_state"],
            "diagnostic_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            "constraint_summary": constraint_summary,
            **REQUIREMENTS_ONLY_FLAGS,
        }
        payloads: dict[str, Any] = {
            **requirements,
            **constraints,
            "go_no_go": go_no_go,
            "coverage": coverage,
            "diagnostics": diagnostics,
            "recommendations": recommendations,
            "summary": summary,
        }
        storage_paths = self.storage.save(payloads)
        report_paths = self.reports.export(payloads)
        return TradingRequirementsRunResult(
            functional=requirements["functional"],
            non_functional=requirements["non_functional"],
            safety=requirements["safety"],
            risk=requirements["risk"],
            compliance=constraints["compliance"],
            operational=constraints["operational"],
            broker=constraints["broker"],
            execution=constraints["execution"],
            monitoring=constraints["monitoring"],
            data=constraints["data"],
            go_no_go=go_no_go,
            coverage=coverage,
            diagnostics=diagnostics,
            recommendations=recommendations,
            summary=summary,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )

    def get_summary(self) -> dict[str, Any]:
        payload = self._read_json("reports", "trading_requirements", "requirements_summary.json")
        return (
            payload
            if isinstance(payload, dict) and payload
            else self.run_full_requirements_specification().summary
        )

    def get_document(self, filename: str, builder) -> dict[str, Any]:
        payload = self._read_json("storage", "trading_requirements", filename)
        return payload if isinstance(payload, dict) and payload else builder()

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
