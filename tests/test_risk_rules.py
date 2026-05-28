"""Tests for individual reusable risk rules."""

from datetime import UTC, datetime

from app.risk.models import DailyRiskState, RiskRejectionReason
from app.risk.rules import (
    MaxConsecutiveLossesRule,
    MaxDailyLossAmountRule,
    MaxDailyLossPercentRule,
    MaxDailyProfitTargetRule,
    MaxSimultaneousPositionsRule,
    MaxTradesPerDayRule,
    MinimumConfidenceRule,
    RiskRuleContext,
    SessionRestrictionRule,
    SymbolWhitelistRule,
    TimeframeWhitelistRule,
)
from app.signals.signal import SignalDirection, TradeSignal


def _signal(
    confidence: float = 0.8,
    symbol: str = "EURUSD",
    timeframe: str = "1m",
    timestamp: datetime | None = None,
) -> TradeSignal:
    return TradeSignal(
        symbol=symbol,
        timeframe=timeframe,
        direction=SignalDirection.CALL,
        confidence=confidence,
        timestamp=timestamp or datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        strategy_name="test_strategy",
    )


def _context(state: DailyRiskState, signal: TradeSignal | None = None) -> RiskRuleContext:
    return RiskRuleContext(
        signal=signal or _signal(),
        state=state,
        state_snapshot=state.snapshot(),
        exposure_snapshot={},
    )


def test_max_trades_per_day_rule_rejects_at_limit() -> None:
    state = DailyRiskState(date="2026-01-01", trades_taken=2)
    result = MaxTradesPerDayRule(max_trades=2).evaluate(_context(state))

    assert result.reason == RiskRejectionReason.MAX_TRADES_PER_DAY


def test_max_consecutive_losses_rule_rejects_at_limit() -> None:
    state = DailyRiskState(date="2026-01-01", current_loss_streak=3)
    result = MaxConsecutiveLossesRule(max_losses=3).evaluate(_context(state))

    assert result.reason == RiskRejectionReason.MAX_CONSECUTIVE_LOSSES


def test_max_daily_loss_amount_rule_rejects() -> None:
    state = DailyRiskState(date="2026-01-01", realized_pnl=-120.0)
    result = MaxDailyLossAmountRule(max_loss_amount=100.0).evaluate(_context(state))

    assert result.reason == RiskRejectionReason.MAX_DAILY_LOSS_AMOUNT


def test_max_daily_loss_percent_rule_rejects() -> None:
    state = DailyRiskState(date="2026-01-01", realized_pnl=-200.0, starting_balance=1000.0)
    result = MaxDailyLossPercentRule(max_loss_percent=0.10).evaluate(_context(state))

    assert result.reason == RiskRejectionReason.MAX_DAILY_LOSS_PERCENT


def test_max_daily_profit_target_rule_rejects() -> None:
    state = DailyRiskState(date="2026-01-01", realized_pnl=300.0)
    result = MaxDailyProfitTargetRule(profit_target=250.0).evaluate(_context(state))

    assert result.reason == RiskRejectionReason.MAX_DAILY_PROFIT_TARGET


def test_max_simultaneous_positions_rule_rejects() -> None:
    state = DailyRiskState(date="2026-01-01", active_positions=1)
    result = MaxSimultaneousPositionsRule(max_positions=1).evaluate(_context(state))

    assert result.reason == RiskRejectionReason.MAX_SIMULTANEOUS_POSITIONS


def test_minimum_confidence_rule_rejects_low_confidence() -> None:
    state = DailyRiskState(date="2026-01-01")
    result = MinimumConfidenceRule(min_confidence=0.7).evaluate(
        _context(state, _signal(confidence=0.5))
    )

    assert result.reason == RiskRejectionReason.MINIMUM_CONFIDENCE


def test_session_restriction_rule_rejects_outside_session() -> None:
    state = DailyRiskState(date="2026-01-01")
    signal = _signal(timestamp=datetime(2026, 1, 1, 22, 0, tzinfo=UTC))
    result = SessionRestrictionRule(("london",)).evaluate(_context(state, signal))

    assert result.reason == RiskRejectionReason.SESSION_RESTRICTED


def test_symbol_whitelist_rule_rejects_unknown_symbol() -> None:
    state = DailyRiskState(date="2026-01-01")
    result = SymbolWhitelistRule(("EURUSD",)).evaluate(_context(state, _signal(symbol="GBPUSD")))

    assert result.reason == RiskRejectionReason.SYMBOL_NOT_ALLOWED


def test_timeframe_whitelist_rule_rejects_unknown_timeframe() -> None:
    state = DailyRiskState(date="2026-01-01")
    result = TimeframeWhitelistRule(("1m",)).evaluate(_context(state, _signal(timeframe="5m")))

    assert result.reason == RiskRejectionReason.TIMEFRAME_NOT_ALLOWED
