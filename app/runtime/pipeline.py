"""Unified candle processing pipeline for batch and streaming runtimes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger

from app.data.models import Candle, CandleSeries
from app.events import RuntimeEvent, StrategyEvent
from app.execution.execution_manager import ExecutionManager, TradeLifecycleState
from app.runtime.health import HealthMonitor
from app.runtime.kill_switch import KillSwitch
from app.runtime.runtime_state import RuntimeState
from app.storage.persistence import PersistenceService
from app.strategies.base_strategy import BaseStrategy


@dataclass(frozen=True)
class CandleProcessingResult:
    """Outcome of one candle processing pass."""

    signal_generated: bool = False
    executed: bool = False
    blocked: bool = False
    opening_settlements: int = 0
    closing_settlements: int = 0
    stopped: bool = False
    errors: list[str] = field(default_factory=list)


class CandleProcessingPipeline:
    """Shared validation, health, strategy, execution, metrics, and persistence flow."""

    def __init__(
        self,
        strategy: BaseStrategy,
        execution_manager: ExecutionManager,
        state: RuntimeState,
        health_monitor: HealthMonitor,
        kill_switch: KillSwitch,
        persistence: PersistenceService | None = None,
    ) -> None:
        self.strategy = strategy
        self.execution_manager = execution_manager
        self.state = state
        self.health_monitor = health_monitor
        self.kill_switch = kill_switch
        self.persistence = persistence

    def process(
        self,
        candle: Candle,
        series: CandleSeries,
        index: int,
        metadata: dict[str, Any] | None = None,
    ) -> CandleProcessingResult:
        """Process one closed candle through the unified runtime path."""
        errors: list[str] = []
        opening_count = 0
        closing_count = 0
        signal_generated = False
        executed = False
        blocked = False
        try:
            self._validate(candle, series, index)
            self.health_monitor.heartbeat()
            opening_settlements = self.execution_manager.settle_ready_positions(candle)
            opening_count = len(opening_settlements)
            self.state.metrics.settled_trades += opening_count
            context = {
                "current_candle": candle,
                "history": series.history_until(index),
                "index": index,
                "series": series,
                **(metadata or {}),
            }
            signal = self.strategy.on_candle(context)
            self.state.metrics.processed_candles += 1
            if signal is not None:
                signal_generated = True
                self.state.metrics.generated_signals += 1
                self._publish(
                    StrategyEvent(
                        event_type="strategy.signal",
                        aggregate_id=signal.strategy_name,
                        timestamp=signal.timestamp,
                        payload={
                            "strategy_name": signal.strategy_name,
                            "symbol": signal.symbol,
                            "timeframe": signal.timeframe,
                            "direction": signal.direction.value,
                            "confidence": signal.confidence,
                            "timestamp": signal.timestamp.isoformat(),
                        },
                    )
                )
                record = self.execution_manager.execute_signal_with_candle(signal, candle)
                if record.state == TradeLifecycleState.EXECUTED:
                    executed = True
                    self.state.metrics.executed_trades += 1
                elif record.state == TradeLifecycleState.BLOCKED:
                    blocked = True
                    self.state.metrics.blocked_trades += 1
            closing_settlements = self.execution_manager.settle_ready_positions(candle)
            closing_count = len(closing_settlements)
            self.state.metrics.settled_trades += closing_count
        except Exception as exc:
            message = str(exc)
            errors.append(message)
            self.state.metrics.runtime_errors += 1
            self.health_monitor.record_failure("runtime_pipeline", message)
            logger.exception("Runtime pipeline error: {}", exc)

        stopped = self._apply_stop_policy()
        self._publish(
            RuntimeEvent(
                event_type="runtime.candle_processed",
                aggregate_id=f"{candle.symbol}:{candle.timeframe}",
                timestamp=candle.timestamp,
                payload={
                    "index": index,
                    "signal_generated": signal_generated,
                    "executed": executed,
                    "blocked": blocked,
                    "errors": errors,
                    "stopped": stopped,
                },
            )
        )
        return CandleProcessingResult(
            signal_generated=signal_generated,
            executed=executed,
            blocked=blocked,
            opening_settlements=opening_count,
            closing_settlements=closing_count,
            stopped=stopped,
            errors=errors,
        )

    def _validate(self, candle: Candle, series: CandleSeries, index: int) -> None:
        if index < 0 or index >= len(series):
            raise ValueError("Candle index is outside the series")
        if series[index] != candle:
            raise ValueError("Candle does not match the series at index")

    def _apply_stop_policy(self) -> bool:
        health_report = self.health_monitor.report()
        risk_events = self.execution_manager.risk_engine.state_snapshot().get(
            "risk_shutdown_events",
            [],
        )
        if self.kill_switch.should_stop(self.state, health_report, list(risk_events)):
            self.state.emergency_stop = True
            self.state.active = False
            return True
        return False

    def _publish(self, event: RuntimeEvent | StrategyEvent) -> None:
        if self.persistence is not None:
            self.persistence.persist_event(event)
