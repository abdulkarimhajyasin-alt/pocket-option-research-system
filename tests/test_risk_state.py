"""Tests for risk state, cooldowns, and exposure tracking."""

from datetime import UTC, datetime, timedelta

from app.backtesting.models import TradeOutcome
from app.risk.exposure import ExposureTracker
from app.risk.models import RiskRejectionReason
from app.risk.risk_engine import RiskConfig, RiskEngine
from app.risk.state_manager import RiskStateManager
from app.signals.signal import SignalDirection, TradeSignal


def _signal(timestamp: datetime | None = None, confidence: float = 0.8) -> TradeSignal:
    return TradeSignal(
        symbol="EURUSD",
        timeframe="1m",
        direction=SignalDirection.CALL,
        confidence=confidence,
        timestamp=timestamp or datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        strategy_name="test_strategy",
    )


def test_state_manager_tracks_loss_streak_and_cooldown() -> None:
    manager = RiskStateManager(starting_balance=1000.0)
    timestamp = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)

    manager.record_trade_outcome(
        outcome=TradeOutcome.LOSS,
        pnl=-1.0,
        timestamp=timestamp,
        strategy_name="test_strategy",
        loss_cooldown_minutes=10,
    )

    assert manager.state.current_loss_streak == 1
    assert manager.state.cooldown_until == timestamp + timedelta(minutes=10)
    assert manager.state.strategy_cooldowns["test_strategy"] == timestamp + timedelta(minutes=10)


def test_state_manager_resets_on_new_utc_day() -> None:
    manager = RiskStateManager(starting_balance=1000.0)
    manager.state.trades_taken = 5

    manager.ensure_date(datetime(2026, 1, 2, 0, 1, tzinfo=UTC))

    assert manager.state.date == "2026-01-02"
    assert manager.state.trades_taken == 0


def test_exposure_tracker_counts_dimensions() -> None:
    tracker = ExposureTracker()
    signal = _signal()

    tracker.register("trade-1", signal)

    assert tracker.total_active() == 1
    assert tracker.symbol_exposure("EURUSD") == 1
    assert tracker.strategy_exposure("test_strategy") == 1
    assert tracker.direction_exposure("call") == 1


def test_risk_engine_rejection_event_is_structured() -> None:
    engine = RiskEngine(
        config=RiskConfig(
            min_confidence=0.9,
            enabled_rules=("minimum_confidence",),
        )
    )

    result = engine.assess_signal(_signal(confidence=0.5))

    assert result.approved is False
    assert result.reason == RiskRejectionReason.MINIMUM_CONFIDENCE
    assert engine.events[-1].reason == RiskRejectionReason.MINIMUM_CONFIDENCE
    assert engine.state_manager.state.blocked_trades == 1


def test_risk_engine_loads_yaml_profile() -> None:
    engine = RiskEngine.from_profile("configs/risk/base_risk.yaml")

    assert engine.config.allowed_symbols == ("EURUSD",)
    assert engine.config.min_confidence == 0.6


def test_risk_engine_blocks_during_loss_cooldown() -> None:
    engine = RiskEngine(
        config=RiskConfig(
            min_confidence=0.6,
            loss_cooldown_minutes=10,
            enabled_rules=("cooldown_after_loss", "minimum_confidence"),
        )
    )
    timestamp = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    engine.record_trade_result(
        outcome=TradeOutcome.LOSS,
        pnl=-1.0,
        timestamp=timestamp,
        strategy_name="test_strategy",
    )

    result = engine.assess_signal(_signal(timestamp=timestamp + timedelta(minutes=5)))

    assert result.approved is False
    assert result.reason == RiskRejectionReason.COOLDOWN_AFTER_LOSS
