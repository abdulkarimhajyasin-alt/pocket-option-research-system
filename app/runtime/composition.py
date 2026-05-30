"""Runtime composition layer for assembling replaceable components."""

from dataclasses import dataclass
from pathlib import Path

from app.config.config_manager import AppConfig
from app.runtime.container import ServiceContainer
from app.runtime.factory import RuntimeDependencyFactory
from app.runtime.runtime_manager import RuntimeConfig, RuntimeManager
from app.runtime.streaming_runtime import StreamingRuntime


@dataclass
class RuntimeComposition:
    """Composed runtime graph for an orchestrated application session."""

    container: ServiceContainer
    runtime_manager: RuntimeManager


class RuntimeComposer:
    """Builds runtime components and wires dependencies."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.factory = RuntimeDependencyFactory(self.project_root)

    def compose(self, config: AppConfig) -> RuntimeComposition:
        """Compose the default paper runtime graph."""
        container = ServiceContainer()
        runtime_config = RuntimeConfig.from_yaml(
            self.project_root / config.environment.runtime_config
        )
        strategy_config = self.factory.create_strategy_config(config.environment.strategy_config)
        strategy_registry = self.factory.create_strategy_registry()
        strategy = strategy_registry.create_from_config(strategy_config)
        runtime_manager = RuntimeManager(
            config=runtime_config,
            strategy=strategy,
            factory=self.factory,
        )
        connector_registry = self.factory.create_connector_registry()
        connectivity_runtime = self.factory.create_connectivity_runtime(
            str(config.get("connectivity.default_connector", "csv_market_connector")),
            stale_after_minutes=int(config.get("connectivity.stale_after_minutes", 1440)),
        )
        streaming_config = self.factory.create_streaming_config(
            "configs/streaming/stream_research.yaml"
        )
        streaming_runtime = StreamingRuntime(
            self.factory.create_stream(streaming_config),
            strategy=strategy,
            execution_manager=runtime_manager.execution_manager,
            state=runtime_manager.state,
            health_monitor=runtime_manager.health_monitor,
            kill_switch=runtime_manager.kill_switch,
            persistence=runtime_manager.persistence,
        )

        container.register_instance("config", config)
        container.register_instance("runtime_config", runtime_config)
        container.register_instance("strategy_registry", strategy_registry)
        container.register_instance("strategy", strategy)
        container.register_instance("runtime_manager", runtime_manager)
        container.register_instance("risk_engine", runtime_manager.risk_engine)
        container.register_instance("broker_runtime", runtime_manager.broker_runtime)
        container.register_instance("analytics", runtime_manager.trade_journal)
        container.register_instance("persistence", runtime_manager.persistence)
        container.register_instance("connector_registry", connector_registry)
        container.register_instance("connectivity_runtime", connectivity_runtime)
        container.register_instance("streaming_config", streaming_config)
        container.register_instance("streaming_runtime", streaming_runtime)
        return RuntimeComposition(container=container, runtime_manager=runtime_manager)
