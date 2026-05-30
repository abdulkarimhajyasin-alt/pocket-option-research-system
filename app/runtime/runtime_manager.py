"""Runtime manager for local paper trading sessions."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from app.data.csv_loader import CsvCandleLoader
from app.runtime.event_loop import RuntimeEventLoop
from app.runtime.factory import RuntimeDependencyFactory
from app.runtime.runtime_state import RuntimeMode, RuntimeState
from app.strategies.base_strategy import BaseStrategy


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime configuration for local paper sessions."""

    runtime_mode: RuntimeMode = RuntimeMode.PAPER
    polling_interval_seconds: float = 0.0
    paper_balance: float = 10_000.0
    payout_percentage: float = 0.80
    stake: float = 1.0
    expiry_candles: int = 1
    max_runtime_errors: int = 5
    stop_on_health_failure: bool = True
    stop_on_risk_shutdown: bool = True
    max_candles: int | None = None
    symbols: list[str] = field(default_factory=lambda: ["EURUSD"])
    timeframe: str = "1m"
    data_path: str = "data/sample_eurusd_m1.csv"
    risk_profile: str = "configs/risk/base_risk.yaml"
    persistence_enabled: bool = True
    database_path: str = "storage/trading_system.db"

    @classmethod
    def from_yaml(cls, path: Path | str) -> "RuntimeConfig":
        """Load runtime configuration from YAML."""
        config_path = Path(path)
        logger.info("Loading runtime config from {}", config_path)
        raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        return cls(
            runtime_mode=RuntimeMode(raw.get("runtime_mode", RuntimeMode.PAPER.value)),
            polling_interval_seconds=float(raw.get("polling_interval_seconds", 0.0)),
            paper_balance=float(raw.get("paper_balance", 10_000.0)),
            payout_percentage=float(raw.get("payout_percentage", 0.80)),
            stake=float(raw.get("stake", 1.0)),
            expiry_candles=int(raw.get("expiry_candles", 1)),
            max_runtime_errors=int(raw.get("max_runtime_errors", 5)),
            stop_on_health_failure=bool(raw.get("stop_on_health_failure", True)),
            stop_on_risk_shutdown=bool(raw.get("stop_on_risk_shutdown", True)),
            max_candles=raw.get("max_candles"),
            symbols=list(raw.get("symbols", ["EURUSD"])),
            timeframe=str(raw.get("timeframe", "1m")),
            data_path=str(raw.get("data_path", "data/sample_eurusd_m1.csv")),
            risk_profile=str(raw.get("risk_profile", "configs/risk/base_risk.yaml")),
            persistence_enabled=bool(raw.get("persistence_enabled", True)),
            database_path=str(raw.get("database_path", "storage/trading_system.db")),
        )


class RuntimeManager:
    """Initializes and coordinates a local paper trading runtime."""

    def __init__(
        self,
        config: RuntimeConfig,
        strategy: BaseStrategy,
        factory: RuntimeDependencyFactory | None = None,
    ) -> None:
        self.config = config
        self.strategy = strategy
        self.factory = factory or RuntimeDependencyFactory()
        self.state = self.factory.create_runtime_state(config)
        self.health_monitor = self.factory.create_health_monitor(config)
        self.kill_switch = self.factory.create_kill_switch(config)
        self.shutdown_manager = self.factory.create_shutdown_manager()
        self.broker = self.factory.create_broker(config)
        self.broker_runtime = self.factory.create_broker_runtime(self.broker)
        self.risk_engine = self.factory.create_risk_engine(config)
        self.trade_journal = self.factory.create_trade_journal()
        self.equity_curve = self.factory.create_equity_curve(config)
        self.execution_manager = self.factory.create_execution_manager(
            config,
            self.risk_engine,
            self.broker,
            self.trade_journal,
            self.equity_curve,
        )
        self.persistence = self.factory.create_persistence(config)

    def run(self) -> RuntimeState:
        """Run the configured local paper runtime."""
        logger.info("Runtime starting mode={}", self.config.runtime_mode.value)
        self.state.start()
        self.broker_runtime.initialize()
        try:
            broker_health = self.broker_runtime.heartbeat()
            self.persistence.persist_broker_health(self.broker.name, broker_health)
            symbol = self.config.symbols[0]
            candles = CsvCandleLoader().load(
                self.config.data_path,
                symbol=symbol,
                timeframe=self.config.timeframe,
            )
            loop = RuntimeEventLoop(
                strategy=self.strategy,
                candles=candles,
                execution_manager=self.execution_manager,
                state=self.state,
                health_monitor=self.health_monitor,
                kill_switch=self.kill_switch,
                persistence=self.persistence,
                polling_interval_seconds=self.config.polling_interval_seconds,
                max_candles=self.config.max_candles,
            )
            loop.run()
        finally:
            self.broker_runtime.shutdown()
            reason = self.kill_switch.reason or "completed"
            self.shutdown_manager.shutdown(self.state, reason=reason)
            self.persistence.persist_runtime_state(self.state)
            self.persistence.persist_trade_journal(self.trade_journal.entries())
            self.persistence.persist_risk_events(self.risk_engine.events)
            self.persistence.snapshots.create_snapshot(
                self.persistence.session_id,
                self.state,
                self.risk_engine,
                self.broker.get_open_positions(),
            )
        return self.state
