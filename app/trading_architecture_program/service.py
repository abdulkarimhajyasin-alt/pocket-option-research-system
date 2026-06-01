"""Service layer for Trading System Architecture Program foundation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.trading_architecture_program.architecture_domains import ArchitectureDomainBuilder
from app.trading_architecture_program.decision_gates import DecisionGateBuilder
from app.trading_architecture_program.diagnostics import TradingArchitectureProgramDiagnostics
from app.trading_architecture_program.governance import ProgramGovernanceBuilder
from app.trading_architecture_program.program_registry import ProgramRegistryBuilder
from app.trading_architecture_program.recommendations import (
    TradingArchitectureProgramRecommendationBuilder,
)
from app.trading_architecture_program.reports import TradingArchitectureProgramReportWriter
from app.trading_architecture_program.schemas import (
    ARCHITECTURE_ONLY_FLAGS,
    PROGRAM_NAME,
    PROGRAM_STATUS,
)
from app.trading_architecture_program.storage import TradingArchitectureProgramStorage
from app.trading_architecture_program.workstreams import ProgramWorkstreamBuilder


@dataclass(frozen=True)
class TradingArchitectureProgramRunResult:
    """Result of one architecture-program generation cycle."""

    registry: dict[str, Any]
    domains: list[dict[str, Any]]
    gates: list[dict[str, Any]]
    workstreams: list[dict[str, Any]]
    diagnostics: list[dict[str, str]]
    recommendations: list[str]
    summary: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class TradingArchitectureProgramService:
    """Generate architecture-only program foundation artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.domain_builder = ArchitectureDomainBuilder()
        self.gate_builder = DecisionGateBuilder()
        self.workstream_builder = ProgramWorkstreamBuilder()
        self.governance_builder = ProgramGovernanceBuilder()
        self.registry_builder = ProgramRegistryBuilder()
        self.diagnostics_builder = TradingArchitectureProgramDiagnostics()
        self.recommendation_builder = TradingArchitectureProgramRecommendationBuilder()
        self.storage = TradingArchitectureProgramStorage(
            self.project_root / "storage" / "trading_architecture_program"
        )
        self.reports = TradingArchitectureProgramReportWriter(
            self.project_root / "reports" / "trading_architecture_program"
        )

    def build_domains(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.domain_builder.build()]

    def build_decision_gates(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.gate_builder.build()]

    def build_workstreams(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.workstream_builder.build()]

    def build_program_registry(self) -> dict[str, Any]:
        return self.registry_builder.build(
            self.build_domains(),
            self.build_workstreams(),
            self.build_decision_gates(),
        ).to_dict()

    def generate_diagnostics(self) -> list[dict[str, str]]:
        domains = self.build_domains()
        gates = self.build_decision_gates()
        workstreams = self.build_workstreams()
        registry = self.registry_builder.build(domains, workstreams, gates).to_dict()
        return self.diagnostics_builder.evaluate(
            self.project_root,
            registry,
            domains,
            gates,
            workstreams,
        )

    def generate_recommendations(self) -> list[str]:
        return self.recommendation_builder.build()

    def run_full_program_foundation(self) -> TradingArchitectureProgramRunResult:
        domains = self.build_domains()
        gates = self.build_decision_gates()
        workstreams = self.build_workstreams()
        registry = self.registry_builder.build(domains, workstreams, gates).to_dict()
        diagnostics = self.diagnostics_builder.evaluate(
            self.project_root,
            registry,
            domains,
            gates,
            workstreams,
        )
        recommendations = self.generate_recommendations()
        summary = self._summary(domains, gates, workstreams, diagnostics, recommendations)
        payloads = {
            "registry": registry,
            "domains": domains,
            "gates": gates,
            "workstreams": workstreams,
            "diagnostics": diagnostics,
            "recommendations": recommendations,
            "summary": summary,
        }
        storage_paths = self.storage.save(payloads)
        report_paths = self.reports.export(payloads)
        return TradingArchitectureProgramRunResult(
            registry=registry,
            domains=domains,
            gates=gates,
            workstreams=workstreams,
            diagnostics=diagnostics,
            recommendations=recommendations,
            summary=summary,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )

    def get_summary(self) -> dict[str, Any]:
        payload = self._read_json(
            "reports",
            "trading_architecture_program",
            "program_summary.json",
        )
        return payload if payload else self.run_full_program_foundation().summary

    def domains(self) -> list[dict[str, Any]]:
        payload = self._read_json("storage", "trading_architecture_program", "domains.json")
        return payload if isinstance(payload, list) else self.build_domains()

    def gates(self) -> list[dict[str, Any]]:
        payload = self._read_json("storage", "trading_architecture_program", "gates.json")
        return payload if isinstance(payload, list) else self.build_decision_gates()

    def workstreams(self) -> list[dict[str, Any]]:
        payload = self._read_json(
            "storage",
            "trading_architecture_program",
            "workstreams.json",
        )
        return payload if isinstance(payload, list) else self.build_workstreams()

    def _summary(
        self,
        domains: list[dict[str, Any]],
        gates: list[dict[str, Any]],
        workstreams: list[dict[str, Any]],
        diagnostics: list[dict[str, str]],
        recommendations: list[str],
    ) -> dict[str, Any]:
        return {
            "program_name": PROGRAM_NAME,
            "program_status": PROGRAM_STATUS,
            "domain_count": len(domains),
            "workstream_count": len(workstreams),
            "gate_count": len(gates),
            "diagnostic_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            "governance": self.governance_builder.build(),
            **ARCHITECTURE_ONLY_FLAGS,
        }

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
