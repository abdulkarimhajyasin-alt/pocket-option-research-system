"""Runtime dependency factory for replaceable local research services."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.analytics.equity_curve import EquityCurveTracker
from app.analytics.trade_journal import TradeJournal
from app.brokers.capabilities import BrokerCapabilities
from app.brokers.demo_adapter import DemoBrokerAdapter
from app.brokers.models import BrokerMode
from app.brokers.paper_broker import PaperBroker
from app.config.strategy_config import StrategyConfig, StrategyConfigLoader
from app.connectivity.csv_market_connector import CsvMarketDataConnector
from app.connectivity.registry import ConnectorRegistry
from app.connectivity.simulated_market_connector import SimulatedMarketConnector
from app.execution.execution_manager import ExecutionManager
from app.risk.risk_engine import RiskEngine
from app.runtime.broker_runtime import BrokerRuntime
from app.runtime.connectivity_runtime import ConnectivityRuntime
from app.runtime.health import HealthMonitor
from app.runtime.kill_switch import KillSwitch, KillSwitchConfig
from app.runtime.runtime_state import RuntimeState
from app.runtime.shutdown import ShutdownManager
from app.storage.persistence import PersistenceService
from app.strategies.base_strategy import BaseStrategy
from app.strategies.registry import StrategyRegistry, default_strategy_registry
from app.streaming.config import StreamingConfig
from app.streaming.simulated_stream import SimulatedMarketStream


class RuntimeDependencyFactory:
    """Creates runtime dependencies from typed configuration."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def create_strategy_config(self, path: Path | str) -> StrategyConfig:
        """Load a strategy configuration."""
        return StrategyConfigLoader().load(self._path(path))

    def create_strategy_registry(self) -> StrategyRegistry:
        """Create the default strategy registry."""
        return default_strategy_registry()

    def create_strategy(self, config: StrategyConfig) -> BaseStrategy:
        """Create a strategy from config."""
        return self.create_strategy_registry().create_from_config(config)

    def create_broker(self, config: Any) -> DemoBrokerAdapter:
        """Create the safe demo broker adapter."""
        return DemoBrokerAdapter(
            paper_broker=PaperBroker(
                initial_balance=config.paper_balance,
                payout_percentage=config.payout_percentage,
                stake=config.stake,
                expiry_candles=config.expiry_candles,
            ),
            capabilities=BrokerCapabilities(
                demo_supported=True,
                live_supported=False,
                supported_symbols=tuple(config.symbols),
                supported_timeframes=(config.timeframe,),
                payout_supported=True,
                trade_types=("binary_option",),
                historical_data_supported=False,
            ),
            mode=BrokerMode.DEMO,
        )

    def create_broker_runtime(self, broker: DemoBrokerAdapter) -> BrokerRuntime:
        """Create broker runtime wrapper."""
        return BrokerRuntime(broker)

    def create_risk_engine(self, config: Any) -> RiskEngine:
        """Create risk engine from the runtime risk profile."""
        return RiskEngine.from_profile(config.risk_profile)

    def create_trade_journal(self) -> TradeJournal:
        """Create trade journal."""
        return TradeJournal()

    def create_equity_curve(self, config: Any) -> EquityCurveTracker:
        """Create equity curve tracker."""
        return EquityCurveTracker(initial_equity=config.paper_balance)

    def create_execution_manager(
        self,
        config: Any,
        risk_engine: RiskEngine,
        broker: DemoBrokerAdapter,
        trade_journal: TradeJournal,
        equity_curve: EquityCurveTracker,
    ) -> ExecutionManager:
        """Create execution manager."""
        return ExecutionManager(
            risk_engine,
            broker,
            trade_journal=trade_journal,
            equity_curve=equity_curve,
            runtime_mode=config.runtime_mode.value,
        )

    def create_persistence(self, config: Any) -> PersistenceService:
        """Create persistence service."""
        return PersistenceService(
            database_path=config.database_path,
            enabled=config.persistence_enabled,
        )

    def create_health_monitor(self, config: Any) -> HealthMonitor:
        """Create health monitor."""
        return HealthMonitor(max_failures=config.max_runtime_errors)

    def create_kill_switch(self, config: Any) -> KillSwitch:
        """Create kill switch."""
        return KillSwitch(
            KillSwitchConfig(
                stop_on_health_failure=config.stop_on_health_failure,
                max_runtime_errors=config.max_runtime_errors,
                stop_on_risk_shutdown=config.stop_on_risk_shutdown,
            )
        )

    def create_runtime_state(self, config: Any) -> RuntimeState:
        """Create runtime state."""
        return RuntimeState(mode=config.runtime_mode)

    def create_shutdown_manager(self) -> ShutdownManager:
        """Create shutdown manager."""
        return ShutdownManager()

    def create_connector_registry(self) -> ConnectorRegistry:
        """Create read-only market data connector registry."""
        registry = ConnectorRegistry()
        registry.register(
            "csv_market_connector",
            lambda: CsvMarketDataConnector.from_yaml(
                self.project_root / "configs/connectivity/csv_connector.yaml"
            ),
        )
        registry.register(
            "simulated_market_connector",
            lambda: SimulatedMarketConnector.from_yaml(
                self.project_root / "configs/connectivity/simulated_connector.yaml"
            ),
        )
        return registry

    def create_connectivity_runtime(
        self,
        connector_name: str,
        stale_after_minutes: int = 1440,
    ) -> ConnectivityRuntime:
        """Create connectivity runtime for a registered connector."""
        registry = self.create_connector_registry()
        connector = registry.create(connector_name)
        return ConnectivityRuntime(connector, stale_after_minutes=stale_after_minutes)

    def create_streaming_config(self, path: Path | str) -> StreamingConfig:
        """Load streaming config."""
        return StreamingConfig.from_yaml(self._path(path))

    def create_stream(self, config: StreamingConfig) -> SimulatedMarketStream:
        """Create safe simulated stream."""
        return SimulatedMarketStream(
            symbol=config.symbols[0],
            timeframes=tuple(config.timeframes),
            update_interval_seconds=config.update_interval_seconds,
            latency_ms=config.latency_ms,
            seed=config.seed,
        )

    def _path(self, path: Path | str) -> Path:
        candidate = Path(path)
        return candidate if candidate.is_absolute() else self.project_root / candidate
