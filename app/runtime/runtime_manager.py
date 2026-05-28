"""Runtime manager for local paper trading sessions."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from app.analytics.equity_curve import EquityCurveTracker
from app.analytics.trade_journal import TradeJournal
from app.brokers.capabilities import BrokerCapabilities
from app.brokers.demo_adapter import DemoBrokerAdapter
from app.brokers.models import BrokerMode
from app.brokers.paper_broker import PaperBroker
from app.data.csv_loader import CsvCandleLoader
from app.execution.execution_manager import ExecutionManager
from app.risk.risk_engine import RiskEngine
from app.runtime.event_loop import RuntimeEventLoop
from app.runtime.broker_runtime import BrokerRuntime
from app.runtime.health import HealthMonitor
from app.runtime.kill_switch import KillSwitch, KillSwitchConfig
from app.runtime.runtime_state import RuntimeMode, RuntimeState
from app.runtime.shutdown import ShutdownManager
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
        )


class RuntimeManager:
    """Initializes and coordinates a local paper trading runtime."""

    def __init__(self, config: RuntimeConfig, strategy: BaseStrategy) -> None:
        self.config = config
        self.strategy = strategy
        self.state = RuntimeState(mode=config.runtime_mode)
        self.health_monitor = HealthMonitor(max_failures=config.max_runtime_errors)
        self.kill_switch = KillSwitch(
            KillSwitchConfig(
                stop_on_health_failure=config.stop_on_health_failure,
                max_runtime_errors=config.max_runtime_errors,
                stop_on_risk_shutdown=config.stop_on_risk_shutdown,
            )
        )
        self.shutdown_manager = ShutdownManager()
        self.broker = DemoBrokerAdapter(
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
        self.broker_runtime = BrokerRuntime(self.broker)
        self.risk_engine = RiskEngine.from_profile(config.risk_profile)
        self.trade_journal = TradeJournal()
        self.equity_curve = EquityCurveTracker(initial_equity=config.paper_balance)
        self.execution_manager = ExecutionManager(
            self.risk_engine,
            self.broker,
            trade_journal=self.trade_journal,
            equity_curve=self.equity_curve,
            runtime_mode=config.runtime_mode.value,
        )

    def run(self) -> RuntimeState:
        """Run the configured local paper runtime."""
        logger.info("Runtime starting mode={}", self.config.runtime_mode.value)
        self.state.start()
        self.broker_runtime.initialize()
        try:
            self.broker_runtime.heartbeat()
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
                polling_interval_seconds=self.config.polling_interval_seconds,
                max_candles=self.config.max_candles,
            )
            loop.run()
        finally:
            self.broker_runtime.shutdown()
            reason = self.kill_switch.reason or "completed"
            self.shutdown_manager.shutdown(self.state, reason=reason)
        return self.state
