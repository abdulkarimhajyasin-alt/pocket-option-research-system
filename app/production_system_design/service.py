"""Service layer for production system design blueprints."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.production_system_design.alerting_strategy import AlertingStrategyBuilder
from app.production_system_design.backup_recovery import BackupRecoveryBuilder
from app.production_system_design.configuration_strategy import ConfigurationStrategyBuilder
from app.production_system_design.database_strategy import DatabaseStrategyBuilder
from app.production_system_design.diagnostics import ProductionSystemDesignDiagnostics
from app.production_system_design.environment_strategy import EnvironmentStrategyBuilder
from app.production_system_design.event_queue_strategy import EventQueueStrategyBuilder
from app.production_system_design.logging_strategy import LoggingStrategyBuilder
from app.production_system_design.monitoring_strategy import MonitoringStrategyBuilder
from app.production_system_design.readiness_gates import ProductionReadinessGateEngine
from app.production_system_design.recommendations import (
    ProductionSystemDesignRecommendationBuilder,
)
from app.production_system_design.release_rollback import ReleaseRollbackBuilder
from app.production_system_design.reports import ProductionSystemDesignReportWriter
from app.production_system_design.runtime_architecture import RuntimeArchitectureBuilder
from app.production_system_design.schemas import DESIGN_ONLY_FLAGS
from app.production_system_design.secrets_strategy import SecretsStrategyBuilder
from app.production_system_design.service_boundaries import ServiceBoundaryBuilder
from app.production_system_design.storage import ProductionSystemDesignStorage
from app.production_system_design.topology import ProductionTopologyBuilder
from app.production_system_design.incident_response import IncidentResponseBuilder


@dataclass(frozen=True)
class ProductionSystemDesignRunResult:
    """Result of one production design generation cycle."""

    payloads: dict[str, Any]
    diagnostics: list[dict[str, str]]
    recommendations: list[str]
    summary: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ProductionSystemDesignEngine:
    """Build all design-only production blueprint documents."""

    def __init__(self) -> None:
        self.builders = {
            "topology": ProductionTopologyBuilder(),
            "service_boundaries": ServiceBoundaryBuilder(),
            "runtime_architecture": RuntimeArchitectureBuilder(),
            "environment_strategy": EnvironmentStrategyBuilder(),
            "configuration_strategy": ConfigurationStrategyBuilder(),
            "secrets_strategy": SecretsStrategyBuilder(),
            "database_strategy": DatabaseStrategyBuilder(),
            "event_queue_strategy": EventQueueStrategyBuilder(),
            "logging_strategy": LoggingStrategyBuilder(),
            "monitoring_strategy": MonitoringStrategyBuilder(),
            "alerting_strategy": AlertingStrategyBuilder(),
            "incident_response": IncidentResponseBuilder(),
            "backup_recovery": BackupRecoveryBuilder(),
            "release_rollback": ReleaseRollbackBuilder(),
        }
        self.readiness = ProductionReadinessGateEngine()

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
        service_boundary_count = len(payloads["service_boundaries"].get("items", []))
        return {
            "design_status": "Design Incomplete",
            "design_domain_count": len(payloads) - 1,
            "service_boundary_count": service_boundary_count,
            "environment_strategy_status": "Design only",
            "configuration_strategy_status": "Design only",
            "secrets_strategy_status": "Design only",
            "database_strategy_status": "Design only",
            "event_queue_strategy_status": "Design only",
            "monitoring_status": "Design only",
            "alerting_status": "Design only",
            "incident_response_status": "Design only",
            "backup_recovery_status": "Design only",
            "release_rollback_status": "Design only",
            "readiness_state": payloads["readiness_gates"]["readiness_state"],
            "diagnostic_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            **DESIGN_ONLY_FLAGS,
        }


class ProductionSystemDesignService:
    """Generate local design-only production blueprint artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.engine = ProductionSystemDesignEngine()
        self.diagnostics_builder = ProductionSystemDesignDiagnostics()
        self.recommendation_builder = ProductionSystemDesignRecommendationBuilder()
        self.storage = ProductionSystemDesignStorage(
            self.project_root / "storage" / "production_system_design"
        )
        self.reports = ProductionSystemDesignReportWriter(
            self.project_root / "reports" / "production_system_design"
        )

    def build_topology(self) -> dict[str, Any]:
        return self.engine.builders["topology"].build().to_dict()

    def build_service_boundaries(self) -> dict[str, Any]:
        return self.engine.builders["service_boundaries"].build().to_dict()

    def build_runtime_architecture(self) -> dict[str, Any]:
        return self.engine.builders["runtime_architecture"].build().to_dict()

    def build_environment_strategy(self) -> dict[str, Any]:
        return self.engine.builders["environment_strategy"].build().to_dict()

    def build_configuration_strategy(self) -> dict[str, Any]:
        return self.engine.builders["configuration_strategy"].build().to_dict()

    def build_secrets_strategy(self) -> dict[str, Any]:
        return self.engine.builders["secrets_strategy"].build().to_dict()

    def build_database_strategy(self) -> dict[str, Any]:
        return self.engine.builders["database_strategy"].build().to_dict()

    def build_event_queue_strategy(self) -> dict[str, Any]:
        return self.engine.builders["event_queue_strategy"].build().to_dict()

    def build_logging_strategy(self) -> dict[str, Any]:
        return self.engine.builders["logging_strategy"].build().to_dict()

    def build_monitoring_strategy(self) -> dict[str, Any]:
        return self.engine.builders["monitoring_strategy"].build().to_dict()

    def build_alerting_strategy(self) -> dict[str, Any]:
        return self.engine.builders["alerting_strategy"].build().to_dict()

    def build_incident_response(self) -> dict[str, Any]:
        return self.engine.builders["incident_response"].build().to_dict()

    def build_backup_recovery(self) -> dict[str, Any]:
        return self.engine.builders["backup_recovery"].build().to_dict()

    def build_release_rollback(self) -> dict[str, Any]:
        return self.engine.builders["release_rollback"].build().to_dict()

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

    def run_full_production_design(self) -> ProductionSystemDesignRunResult:
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
        return ProductionSystemDesignRunResult(
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
            "production_system_design",
            "production_design_summary.json",
        )
        if isinstance(payload, dict) and payload:
            return payload
        return self.run_full_production_design().summary

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
