"""Candle-by-candle local runtime event loop."""

from time import sleep

from loguru import logger

from app.data.models import CandleSeries
from app.execution.execution_manager import ExecutionManager, TradeLifecycleState
from app.runtime.health import HealthMonitor
from app.runtime.kill_switch import KillSwitch
from app.runtime.runtime_state import RuntimeState
from app.strategies.base_strategy import BaseStrategy


class RuntimeEventLoop:
    """Processes candles through strategy, risk, execution, settlement, and metrics cycles."""

    def __init__(
        self,
        strategy: BaseStrategy,
        candles: CandleSeries,
        execution_manager: ExecutionManager,
        state: RuntimeState,
        health_monitor: HealthMonitor,
        kill_switch: KillSwitch,
        polling_interval_seconds: float = 0.0,
        max_candles: int | None = None,
    ) -> None:
        self.strategy = strategy
        self.candles = candles
        self.execution_manager = execution_manager
        self.state = state
        self.health_monitor = health_monitor
        self.kill_switch = kill_switch
        self.polling_interval_seconds = polling_interval_seconds
        self.max_candles = max_candles

    def run(self) -> None:
        """Run the local candle event loop."""
        logger.info("Runtime event loop started candles={}", len(self.candles))
        for index, candle in enumerate(self.candles):
            if self.max_candles is not None and index >= self.max_candles:
                break
            if not self.state.active:
                break

            try:
                self.health_monitor.heartbeat()
                opening_settlements = self.execution_manager.settle_ready_positions(candle)
                self.state.metrics.settled_trades += len(opening_settlements)
                context = {
                    "current_candle": candle,
                    "history": self.candles.history_until(index),
                    "index": index,
                    "series": self.candles,
                }
                signal = self.strategy.on_candle(context)
                self.state.metrics.processed_candles += 1
                if signal is not None:
                    self.state.metrics.generated_signals += 1
                    record = self.execution_manager.execute_signal_with_candle(signal, candle)
                    if record.state == TradeLifecycleState.EXECUTED:
                        self.state.metrics.executed_trades += 1
                    elif record.state == TradeLifecycleState.BLOCKED:
                        self.state.metrics.blocked_trades += 1
                settlements = self.execution_manager.settle_ready_positions(candle)
                self.state.metrics.settled_trades += len(settlements)
            except Exception as exc:
                self.state.metrics.runtime_errors += 1
                self.health_monitor.record_failure("runtime_loop", str(exc))
                logger.exception("Runtime loop error: {}", exc)

            health_report = self.health_monitor.report()
            risk_events = self.execution_manager.risk_engine.state_snapshot().get(
                "risk_shutdown_events",
                [],
            )
            if self.kill_switch.should_stop(self.state, health_report, list(risk_events)):
                self.state.emergency_stop = True
                self.state.active = False
                break
            if self.polling_interval_seconds > 0:
                sleep(self.polling_interval_seconds)
        logger.info("Runtime event loop completed")
