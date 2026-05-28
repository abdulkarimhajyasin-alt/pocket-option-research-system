"""Execution manager for validated demo signals."""

from typing import Any

from loguru import logger

from app.brokers.base_broker import BaseBroker
from app.risk.risk_engine import RiskEngine
from app.signals.signal import TradeSignal


class ExecutionManager:
    """Coordinates risk checks and demo broker execution."""

    def __init__(self, risk_engine: RiskEngine, broker: BaseBroker) -> None:
        self.risk_engine = risk_engine
        self.broker = broker

    def execute_signal(self, signal: TradeSignal) -> dict[str, Any] | None:
        """Validate and execute a signal through the configured broker."""
        logger.info(
            "Received signal: {} {} {} confidence={}",
            signal.symbol,
            signal.timeframe,
            signal.direction.value,
            signal.confidence,
        )

        if not self.risk_engine.validate_signal(signal):
            logger.warning("Execution skipped by risk engine")
            return None

        execution_result = self.broker.place_trade(signal)
        logger.info("Execution result: {}", execution_result)
        return execution_result
