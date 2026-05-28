"""Execution manager for risk-first local and future broker workflows."""

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from loguru import logger

from app.backtesting.models import TradeOutcome
from app.brokers.base_broker import BaseBroker
from app.data.models import Candle
from app.risk.risk_engine import RiskEngine
from app.signals.signal import TradeSignal


class TradeLifecycleState(StrEnum):
    """Execution lifecycle states."""

    PENDING = "pending"
    EXECUTED = "executed"
    SETTLED = "settled"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class ExecutionRecord:
    """Tracks one signal through execution lifecycle."""

    signal: TradeSignal
    state: TradeLifecycleState
    created_at: datetime
    trade_id: str | None = None
    reason: str | None = None
    result: dict[str, Any] | None = None


class ExecutionManager:
    """Coordinates risk validation, broker execution, and settlement."""

    def __init__(self, risk_engine: RiskEngine, broker: BaseBroker) -> None:
        self.risk_engine = risk_engine
        self.broker = broker
        self.execution_queue: deque[tuple[TradeSignal, Candle | None]] = deque()
        self.records: dict[str, ExecutionRecord] = {}
        self.pending_trade_ids: set[str] = set()

    def enqueue_signal(self, signal: TradeSignal, candle: Candle | None = None) -> None:
        """Add a signal to the execution queue."""
        key = self._signal_key(signal)
        if key in self.records:
            logger.warning("Duplicate execution prevented for {}", key)
            return
        self.records[key] = ExecutionRecord(signal, TradeLifecycleState.PENDING, signal.timestamp)
        self.execution_queue.append((signal, candle))
        logger.info("Signal queued for execution: {}", key)

    def process_queue(self) -> list[ExecutionRecord]:
        """Process all queued signals."""
        processed: list[ExecutionRecord] = []
        while self.execution_queue:
            signal, candle = self.execution_queue.popleft()
            processed.append(self._execute(signal, candle))
        return processed

    def execute_signal(self, signal: TradeSignal) -> dict[str, Any] | None:
        """Backward-compatible immediate execution path."""
        self.enqueue_signal(signal)
        records = self.process_queue()
        record = records[-1] if records else None
        return record.result if record and record.state == TradeLifecycleState.EXECUTED else None

    def execute_signal_with_candle(
        self,
        signal: TradeSignal,
        candle: Candle,
    ) -> ExecutionRecord:
        """Queue and execute one signal with candle context."""
        self.enqueue_signal(signal, candle)
        records = self.process_queue()
        return records[-1]

    def settle_ready_positions(self, candle: Candle) -> list[dict[str, Any]]:
        """Settle broker positions whose expiry has arrived."""
        settlements: list[dict[str, Any]] = []
        get_positions = getattr(self.broker, "get_open_positions", None)
        settle_trade = getattr(self.broker, "settle_trade", None)
        if get_positions is None or settle_trade is None:
            return settlements

        for position in list(get_positions()):
            if candle.timestamp < position.expiry_timestamp:
                continue
            settlement = settle_trade(position.trade_id, candle)
            self.pending_trade_ids.discard(position.trade_id)
            self._mark_settled(position.trade_id, settlement)
            outcome = TradeOutcome(settlement["outcome"])
            self.risk_engine.record_trade_result(
                outcome=outcome,
                pnl=float(settlement["pnl"]),
                timestamp=candle.timestamp,
                strategy_name=position.strategy_name,
            )
            settlements.append(settlement)
        return settlements

    def _execute(self, signal: TradeSignal, candle: Candle | None) -> ExecutionRecord:
        key = self._signal_key(signal)
        record = self.records[key]
        risk_result = self.risk_engine.assess_signal(signal)
        if not risk_result.approved:
            record.state = TradeLifecycleState.BLOCKED
            record.reason = risk_result.reason.value if risk_result.reason else "risk_rejected"
            logger.warning("Execution blocked by risk engine: {}", record.reason)
            return record

        try:
            place_trade = getattr(self.broker, "place_trade")
            try:
                result = place_trade(signal, candle)
            except TypeError:
                result = place_trade(signal)
            record.trade_id = result.get("trade_id")
            record.result = result
            record.state = TradeLifecycleState.EXECUTED
            if record.trade_id:
                self.pending_trade_ids.add(record.trade_id)
            logger.info("Execution completed: {}", result)
        except Exception as exc:
            record.state = TradeLifecycleState.FAILED
            record.reason = str(exc)
            logger.exception("Execution failed: {}", exc)
        return record

    def _mark_settled(self, trade_id: str, settlement: dict[str, Any]) -> None:
        for record in self.records.values():
            if record.trade_id == trade_id:
                record.state = TradeLifecycleState.SETTLED
                record.result = settlement
                return

    def _signal_key(self, signal: TradeSignal) -> str:
        return (
            f"{signal.strategy_name}:{signal.symbol}:{signal.timeframe}:"
            f"{signal.direction.value}:{signal.timestamp.isoformat()}"
        )
