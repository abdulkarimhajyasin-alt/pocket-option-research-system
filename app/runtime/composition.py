"""Runtime composition layer for assembling replaceable components."""

from dataclasses import dataclass
from pathlib import Path

from app.config.config_manager import AppConfig
from app.config.strategy_config import StrategyConfigLoader
from app.connectivity.csv_market_connector import CsvMarketDataConnector
from app.connectivity.registry import ConnectorRegistry
from app.connectivity.simulated_market_connector import SimulatedMarketConnector
from app.runtime.connectivity_runtime import ConnectivityRuntime
from app.runtime.container import ServiceContainer
from app.runtime.runtime_manager import RuntimeConfig, RuntimeManager
from app.runtime.streaming_runtime import StreamingRuntime
from app.strategies.registry import default_strategy_registry
from app.streaming.config import StreamingConfig
from app.streaming.simulated_stream import SimulatedMarketStream


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
        connector_registry = ConnectorRegistry()
        connector_registry.register(
            "csv_market_connector",
            lambda: CsvMarketDataConnector.from_yaml(
                self.project_root / "configs/connectivity/csv_connector.yaml"
            ),
        )
        connector_registry.register(
            "simulated_market_connector",
            lambda: SimulatedMarketConnector.from_yaml(
                self.project_root / "configs/connectivity/simulated_connector.yaml"
            ),
        )
        connector = connector_registry.create(
            str(config.get("connectivity.default_connector", "csv_market_connector"))
        )
        connectivity_runtime = ConnectivityRuntime(
            connector,
            stale_after_minutes=int(config.get("connectivity.stale_after_minutes", 1440)),
        )
        streaming_config = StreamingConfig.from_yaml(
            self.project_root / "configs/streaming/stream_research.yaml"
        )
        streaming_runtime = StreamingRuntime(
            SimulatedMarketStream(
                symbol=streaming_config.symbols[0],
                timeframes=tuple(streaming_config.timeframes),
                update_interval_seconds=streaming_config.update_interval_seconds,
                latency_ms=streaming_config.latency_ms,
                seed=streaming_config.seed,
            )
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
