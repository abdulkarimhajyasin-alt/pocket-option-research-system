"""Smoke tests for the Phase 1 foundation."""

from datetime import UTC, datetime

from app.brokers.mock_broker import MockBroker
from app.execution.execution_manager import ExecutionManager
from app.risk.risk_engine import RiskEngine
from app.signals.signal import SignalDirection, TradeSignal


def test_execution_manager_simulates_valid_signal() -> None:
    """A valid signal should pass risk checks and execute on the mock broker."""
    broker = MockBroker(initial_balance=1_000.0)
    risk_engine = RiskEngine(min_confidence=0.6)
    execution_manager = ExecutionManager(risk_engine=risk_engine, broker=broker)
    signal = TradeSignal(
        symbol="EURUSD",
        timeframe="1m",
        direction=SignalDirection.CALL,
        confidence=0.8,
        timestamp=datetime.now(tz=UTC),
        strategy_name="test_strategy",
    )

    broker.connect()
    result = execution_manager.execute_signal(signal)
    broker.disconnect()

    assert result is not None
    assert result["status"] == "simulated"
    assert result["symbol"] == "EURUSD"


def test_risk_engine_rejects_low_confidence_signal() -> None:
    """Low-confidence signals should be rejected by placeholder risk rules."""
    risk_engine = RiskEngine(min_confidence=0.6)
    signal = TradeSignal(
        symbol="EURUSD",
        timeframe="1m",
        direction=SignalDirection.PUT,
        confidence=0.2,
        timestamp=datetime.now(tz=UTC),
        strategy_name="test_strategy",
    )

    assert risk_engine.validate_signal(signal) is False
