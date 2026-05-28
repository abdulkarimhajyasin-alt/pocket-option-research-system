"""Operational diagnostics report generation."""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from loguru import logger

from app.config.config_manager import AppConfig
from app.runtime.container import ServiceContainer
from app.runtime.startup_checks import StartupValidationResult


@dataclass(frozen=True)
class DiagnosticsReport:
    """Structured diagnostics report for startup and runtime composition."""

    generated_at: datetime
    environment: str
    mode: str
    config: dict[str, Any]
    startup: dict[str, Any]
    dependency_graph: dict[str, Any]
    broker: dict[str, Any] = field(default_factory=dict)
    persistence: dict[str, Any] = field(default_factory=dict)
    connectivity: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable diagnostics payload."""
        return {
            "generated_at": self.generated_at.isoformat(),
            "environment": self.environment,
            "mode": self.mode,
            "config": self.config,
            "startup": self.startup,
            "dependency_graph": self.dependency_graph,
            "broker": self.broker,
            "persistence": self.persistence,
            "connectivity": self.connectivity,
        }


class DiagnosticsBuilder:
    """Builds and exports operational diagnostics reports."""

    def __init__(self, export_dir: Path | str = "reports/diagnostics") -> None:
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def build(
        self,
        config: AppConfig,
        startup: StartupValidationResult,
        container: ServiceContainer | None = None,
    ) -> DiagnosticsReport:
        """Build diagnostics from resolved config and service graph."""
        broker = config.section("broker")
        storage = config.section("storage")
        connectivity = config.section("connectivity")
        connectivity_runtime = None
        if container is not None and "connectivity_runtime" in container.names():
            connectivity_runtime = container.get("connectivity_runtime")
        connectivity_health = (
            connectivity_runtime.diagnostics().__dict__ if connectivity_runtime else {}
        )
        return DiagnosticsReport(
            generated_at=datetime.now(tz=UTC),
            environment=config.environment.name.value,
            mode=config.environment.mode,
            config={
                "runtime_config": config.environment.runtime_config,
                "strategy_config": config.environment.strategy_config,
                "risk_config": config.environment.risk_config,
                "broker_config": config.environment.broker_config,
                "storage_config": config.environment.storage_config,
                "connectivity_config": config.environment.connectivity_config,
            },
            startup={
                "passed": startup.passed,
                "warnings": startup.warnings,
                "failures": startup.failures,
                "checks": [check.__dict__ for check in startup.checks],
            },
            dependency_graph=container.dependency_graph() if container else {},
            broker={
                "mode": broker.get("mode"),
                "capabilities": broker.get("capabilities", {}),
            },
            persistence={
                "enabled": storage.get("enabled", True),
                "database_path": storage.get("database_path"),
            },
            connectivity={
                "read_only": connectivity.get("read_only", True),
                "default_connector": connectivity.get("default_connector"),
                "connectors": connectivity.get("connectors", {}),
                "execution_enabled": connectivity.get("execution_enabled", False),
                "health": connectivity_health,
            },
        )

    def export(self, report: DiagnosticsReport, name: str = "environment") -> Path:
        """Export diagnostics as JSON."""
        path = self.export_dir / f"{name}_diagnostics.json"
        path.write_text(json.dumps(report.to_dict(), indent=2, default=str), encoding="utf-8")
        logger.bind(component="orchestrator").info("Diagnostics exported: {}", path)
        return path
