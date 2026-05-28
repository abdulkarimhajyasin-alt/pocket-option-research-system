"""Tests for execution lifecycle and runtime components."""

from datetime import UTC, datetime

from app.brokers.paper_broker import PaperBroker
from app.data.models import Candle, CandleSeries
from app.execution.execution_manager import ExecutionManager, TradeLifecycleState
from app.execution.positions import Position, PositionStatus, PositionTracker
from app.risk.risk_engine import RiskConfig, RiskEngine
from app.runtime.event_loop import RuntimeEventLoop
from app.runtime.health import HealthMonitor
from app.runtime.kill_switch import KillSwitch
from app.runtime.runtime_state import RuntimeMode, RuntimeState
from app.runtime.shutdown import ShutdownManager
from app.signals.signal import SignalDirection, TradeSignal
from app.strategies.sample_strategy import SampleCandleDirectionStrategy


def _candle(index: int, open_price: float, close: float) -> Candle:
    return Candle(
        symbol="EURUSD",
        timeframe="1m",
        timestamp=datetime(2026, 1, 1, 12, index, tzinfo=UTC),
        open=open_price,
        high=max(open_price, close) + 0.0002,
        low=min(open_price, close) - 0.0002,
        close=close,
    )


def _signal(confidence: float = 0.8) -> TradeSignal:
    return TradeSignal(
        symbol="EURUSD",
        timeframe="1m",
        direction=SignalDirection.CALL,
        confidence=confidence,
        timestamp=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        strategy_name="test_strategy",
    )


def test_execution_manager_blocks_low_confidence_signal() -> None:
    broker = PaperBroker()
    broker.connect()
    risk = RiskEngine(config=RiskConfig(min_confidence=0.9, enabled_rules=("minimum_confidence",)))
    manager = ExecutionManager(risk, broker)

    record = manager.execute_signal_with_candle(_signal(confidence=0.2), _candle(0, 1.1, 1.2))

    assert record.state == TradeLifecycleState.BLOCKED


def test_execution_manager_executes_and_settles_trade() -> None:
    broker = PaperBroker(initial_balance=100.0, stake=10.0)
    broker.connect()
    risk = RiskEngine(config=RiskConfig(enabled_rules=("minimum_confidence",)))
    manager = ExecutionManager(risk, broker)

    record = manager.execute_signal_with_candle(_signal(), _candle(0, 1.1, 1.1))
    settlements = manager.settle_ready_positions(_candle(1, 1.1, 1.2))

    assert record.state == TradeLifecycleState.SETTLED
    assert settlements[0]["outcome"] == "win"


def test_position_tracker_tracks_open_and_closed_positions() -> None:
    tracker = PositionTracker()
    position = Position(
        trade_id="1",
        symbol="EURUSD",
        timeframe="1m",
        direction="call",
        strategy_name="test",
        entry_price=1.1,
        stake=1.0,
        opened_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        expiry_timestamp=datetime(2026, 1, 1, 12, 1, tzinfo=UTC),
    )

    tracker.open(position)
    closed = tracker.close("1", 1.2, 0.8, datetime(2026, 1, 1, 12, 1, tzinfo=UTC))

    assert closed.status == PositionStatus.CLOSED
    assert tracker.symbol_exposure("EURUSD") == 0


def test_runtime_event_loop_processes_candles() -> None:
    candles = CandleSeries(
        "EURUSD",
        "1m",
        [_candle(0, 1.1, 1.2), _candle(1, 1.2, 1.1), _candle(2, 1.1, 1.2)],
    )
    broker = PaperBroker()
    broker.connect()
    risk = RiskEngine(config=RiskConfig(max_trades_per_day=10))
    manager = ExecutionManager(risk, broker)
    state = RuntimeState(mode=RuntimeMode.PAPER)
    state.start()

    RuntimeEventLoop(
        strategy=SampleCandleDirectionStrategy(),
        candles=candles,
        execution_manager=manager,
        state=state,
        health_monitor=HealthMonitor(),
        kill_switch=KillSwitch(),
    ).run()

    assert state.metrics.processed_candles == 3
    assert state.metrics.generated_signals >= 1


def test_kill_switch_manual_stop_and_shutdown() -> None:
    state = RuntimeState(mode=RuntimeMode.PAPER)
    state.start()
    kill_switch = KillSwitch()
    kill_switch.emergency_stop("test")

    assert kill_switch.should_stop(state, HealthMonitor().report()) is True
    ShutdownManager().shutdown(state, "test")
    assert state.active is False
