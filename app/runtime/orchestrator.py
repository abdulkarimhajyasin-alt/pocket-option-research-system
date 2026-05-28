"""Application runtime orchestrator."""

from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from app.config.config_manager import AppConfig, ConfigManager
from app.runtime.composition import RuntimeComposer, RuntimeComposition
from app.runtime.diagnostics import DiagnosticsBuilder, DiagnosticsReport
from app.runtime.runtime_state import RuntimeState
from app.runtime.startup_checks import StartupValidationResult, StartupValidator


@dataclass
class OrchestratorState:
    """Tracks orchestrator bootstrap state."""

    bootstrapped: bool = False
    started: bool = False
    shutdown_complete: bool = False


class RuntimeOrchestrator:
    """Coordinates config loading, startup validation, composition, and runtime lifecycle."""

    def __init__(self, project_root: Path | str = ".", environment: str = "local") -> None:
        self.project_root = Path(project_root)
        self.environment = environment
        self.config_manager = ConfigManager(self.project_root)
        self.startup_validator = StartupValidator(self.project_root)
        self.composer = RuntimeComposer(self.project_root)
        self.diagnostics_builder = DiagnosticsBuilder(self.project_root / "reports" / "diagnostics")
        self.state = OrchestratorState()
        self.config: AppConfig | None = None
        self.startup_result: StartupValidationResult | None = None
        self.composition: RuntimeComposition | None = None

    def bootstrap(self) -> DiagnosticsReport:
        """Load configuration, validate startup, and compose services."""
        logger.bind(component="orchestrator").info(
            "Orchestrator bootstrap environment={}",
            self.environment,
        )
        self.config = self.config_manager.load(self.environment)
        self.startup_result = self.startup_validator.validate(self.config)
        if not self.startup_result.passed:
            diagnostics = self.diagnostics_builder.build(self.config, self.startup_result)
            self.diagnostics_builder.export(diagnostics, self.environment)
            raise RuntimeError(f"Startup validation failed: {self.startup_result.failures}")
        self.composition = self.composer.compose(self.config)
        self.state.bootstrapped = True
        diagnostics = self.diagnostics()
        self.diagnostics_builder.export(diagnostics, self.environment)
        return diagnostics

    def start(self) -> RuntimeState:
        """Start the composed runtime lifecycle."""
        if not self.state.bootstrapped:
            self.bootstrap()
        if self.composition is None:
            raise RuntimeError("Runtime composition is not available")
        logger.bind(component="orchestrator").info("Starting orchestrated runtime")
        self.state.started = True
        return self.composition.runtime_manager.run()

    def shutdown(self) -> None:
        """Coordinate safe orchestrator shutdown."""
        logger.bind(component="orchestrator").info("Orchestrator shutdown")
        if self.composition is not None:
            self.composition.runtime_manager.persistence.close()
        self.state.shutdown_complete = True

    def diagnostics(self) -> DiagnosticsReport:
        """Return current diagnostics report."""
        if self.config is None or self.startup_result is None:
            raise RuntimeError("Orchestrator has not been bootstrapped")
        container = self.composition.container if self.composition else None
        return self.diagnostics_builder.build(self.config, self.startup_result, container)
