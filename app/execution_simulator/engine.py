"""Offline binary outcome and execution simulation engines."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.data.models import Candle, CandleSeries
from app.execution_simulator.models import (
    BinaryOutcome,
    ExpiryDuration,
    SimulatedOrder,
    SimulatedTrade,
)
from app.safety.gates import SafetyGateResult, SafetyGateService
from app.signals.signal import SignalDirection, TradeSignal


@dataclass(frozen=True)
class BinaryOutcomeEngine:
    """Deterministically evaluate a simulated binary-options outcome."""

    allow_draw: bool = True

    def evaluate(
        self,
        order: SimulatedOrder,
        entry_candle: Candle,
        expiry_candle: Candle,
    ) -> SimulatedTrade:
        """Evaluate one order using historical entry and expiry candles only."""
        outcome = self._outcome(
            order.direction,
            entry_candle.close,
            expiry_candle.close,
        )
        payout, profit_loss = self._payout(order.stake, order.payout_ratio, outcome)
        expected_return = (order.confidence * order.payout_ratio) - (1 - order.confidence)
        actual_return = profit_loss / order.stake if order.stake else 0.0
        return SimulatedTrade(
            trade_id=f"trade-{uuid4()}",
            order_id=order.order_id,
            symbol=order.symbol,
            timeframe=order.timeframe,
            direction=order.direction.value,
            strategy_name=order.strategy_name,
            confidence=order.confidence,
            entry_time=entry_candle.timestamp,
            expiry_time=expiry_candle.timestamp,
            entry_price=entry_candle.close,
            expiry_price=expiry_candle.close,
            outcome=outcome,
            payout=round(payout, 8),
            profit_loss=round(profit_loss, 8),
            expected_return=round(expected_return, 8),
            actual_return=round(actual_return, 8),
        )

    def _outcome(
        self,
        direction: SignalDirection,
        entry_price: float,
        expiry_price: float,
    ) -> BinaryOutcome:
        if expiry_price == entry_price and self.allow_draw:
            return BinaryOutcome.DRAW
        if direction == SignalDirection.CALL:
            return BinaryOutcome.WIN if expiry_price > entry_price else BinaryOutcome.LOSS
        if direction == SignalDirection.PUT:
            return BinaryOutcome.WIN if expiry_price < entry_price else BinaryOutcome.LOSS
        return BinaryOutcome.LOSS

    def _payout(
        self,
        stake: float,
        payout_ratio: float,
        outcome: BinaryOutcome,
    ) -> tuple[float, float]:
        if outcome == BinaryOutcome.WIN:
            payout = stake * payout_ratio
            return payout, payout
        if outcome == BinaryOutcome.DRAW:
            return stake, 0.0
        return 0.0, -stake


@dataclass
class ExecutionSimulator:
    """Bridge strategy signals into local-only simulated execution."""

    safety: SafetyGateService
    outcome_engine: BinaryOutcomeEngine = BinaryOutcomeEngine()
    expiry: ExpiryDuration = ExpiryDuration.MINUTES_1
    stake: float = 1.0
    payout_ratio: float = 0.80

    def simulate_signal(
        self,
        signal: TradeSignal,
        candles: CandleSeries,
        entry_index: int,
    ) -> SimulatedTrade:
        """Apply safety gates and simulate one signal outcome."""
        entry_candle = candles[entry_index]
        order = SimulatedOrder.create(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            direction=signal.direction,
            confidence=signal.confidence,
            requested_at=signal.timestamp,
            strategy_name=signal.strategy_name,
            expiry=self.expiry,
            stake=self.stake,
            payout_ratio=self.payout_ratio,
        )
        safety_result = self.safety.evaluate_signal(signal)
        if not safety_result.approved:
            return self._blocked_trade(order, entry_candle, safety_result)
        expiry_index = self._expiry_index(candles, entry_index, self.expiry)
        if expiry_index is None:
            return self._skipped_trade(order, entry_candle, "insufficient_future_candles")
        trade = self.outcome_engine.evaluate(order, entry_candle, candles[expiry_index])
        self.safety.record_trade(trade)
        return trade

    def _expiry_index(
        self,
        candles: CandleSeries,
        entry_index: int,
        expiry: ExpiryDuration,
    ) -> int | None:
        target_time = candles[entry_index].timestamp + expiry.delta
        for index in range(entry_index + 1, len(candles)):
            if candles[index].timestamp >= target_time:
                return index
        return None

    def _blocked_trade(
        self,
        order: SimulatedOrder,
        entry_candle: Candle,
        safety_result: SafetyGateResult,
    ) -> SimulatedTrade:
        return SimulatedTrade(
            trade_id=f"trade-{uuid4()}",
            order_id=order.order_id,
            symbol=order.symbol,
            timeframe=order.timeframe,
            direction=order.direction.value,
            strategy_name=order.strategy_name,
            confidence=order.confidence,
            entry_time=entry_candle.timestamp,
            expiry_time=None,
            entry_price=entry_candle.close,
            expiry_price=None,
            outcome=BinaryOutcome.BLOCKED,
            payout=0.0,
            profit_loss=0.0,
            expected_return=0.0,
            actual_return=0.0,
            blocked_reason=safety_result.reason,
        )

    def _skipped_trade(
        self,
        order: SimulatedOrder,
        entry_candle: Candle,
        reason: str,
    ) -> SimulatedTrade:
        return SimulatedTrade(
            trade_id=f"trade-{uuid4()}",
            order_id=order.order_id,
            symbol=order.symbol,
            timeframe=order.timeframe,
            direction=order.direction.value,
            strategy_name=order.strategy_name,
            confidence=order.confidence,
            entry_time=entry_candle.timestamp,
            expiry_time=None,
            entry_price=entry_candle.close,
            expiry_price=None,
            outcome=BinaryOutcome.SKIPPED,
            payout=0.0,
            profit_loss=0.0,
            expected_return=0.0,
            actual_return=0.0,
            blocked_reason=reason,
        )
