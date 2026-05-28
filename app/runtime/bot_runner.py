"""Minimal runtime flow for Phase 1 architecture validation."""

from datetime import UTC, datetime

from loguru import logger

from app.brokers.mock_broker import MockBroker
from app.config.settings import Settings
from app.execution.execution_manager import ExecutionManager
from app.logging.logger import configure_logging
from app.risk.risk_engine import RiskEngine
from app.signals.signal import SignalDirection, TradeSignal


class BotRunner:
    """Coordinates the minimal demo-only platform runtime."""

    def __init__(self) -> None:
        self.settings = Settings()
        configure_logging(self.settings.log_level, self.settings.log_file_path)

    def run(self) -> None:
        """Run a single simulated signal execution."""
        logger.info("Starting Phase 1 research platform demo flow")

        broker = MockBroker(initial_balance=self.settings.mock_initial_balance)
        risk_engine = RiskEngine(min_confidence=self.settings.min_signal_confidence)
        execution_manager = ExecutionManager(risk_engine=risk_engine, broker=broker)

        broker.connect()
        signal = TradeSignal(
            symbol="EURUSD",
            timeframe="1m",
            direction=SignalDirection.CALL,
            confidence=0.82,
            timestamp=datetime.now(tz=UTC),
            strategy_name="phase_1_demo_strategy",
        )

        execution_manager.execute_signal(signal)
        broker.disconnect()

        logger.info("Phase 1 demo flow completed")
