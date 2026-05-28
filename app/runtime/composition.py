"""Runtime composition layer for assembling replaceable components."""

from dataclasses import dataclass
from pathlib import Path

from app.config.config_manager import AppConfig
from app.config.strategy_config import StrategyConfigLoader
from app.runtime.container import ServiceContainer
from app.runtime.runtime_manager import RuntimeConfig, RuntimeManager
from app.strategies.registry import default_strategy_registry


@dataclass
class RuntimeComposition:
    """Composed runtime graph for an orchestrated application session."""

    container: ServiceContainer
    runtime_manager: RuntimeManager


class RuntimeComposer:
    """Builds runtime components and wires dependencies."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def compose(self, config: AppConfig) -> RuntimeComposition:
        """Compose the default paper runtime graph."""
        container = ServiceContainer()
        runtime_config = RuntimeConfig.from_yaml(
            self.project_root / config.environment.runtime_config
        )
        strategy_config = StrategyConfigLoader().load(
            self.project_root / config.environment.strategy_config
        )
        strategy_registry = default_strategy_registry()
        strategy = strategy_registry.create_from_config(strategy_config)
        runtime_manager = RuntimeManager(config=runtime_config, strategy=strategy)

        container.register_instance("config", config)
        container.register_instance("runtime_config", runtime_config)
        container.register_instance("strategy_registry", strategy_registry)
        container.register_instance("strategy", strategy)
        container.register_instance("runtime_manager", runtime_manager)
        container.register_instance("risk_engine", runtime_manager.risk_engine)
        container.register_instance("broker_runtime", runtime_manager.broker_runtime)
        container.register_instance("analytics", runtime_manager.trade_journal)
        container.register_instance("persistence", runtime_manager.persistence)
        return RuntimeComposition(container=container, runtime_manager=runtime_manager)
