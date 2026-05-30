"""Candle-by-candle local runtime event loop."""

from collections.abc import Iterable
from time import sleep

from loguru import logger

from app.data.models import CandleSeries
from app.execution.execution_manager import ExecutionManager
from app.runtime.health import HealthMonitor
from app.runtime.kill_switch import KillSwitch
from app.runtime.pipeline import CandleProcessingPipeline
from app.runtime.runtime_state import RuntimeState
from app.storage.persistence import PersistenceService
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
        persistence: PersistenceService | None = None,
        polling_interval_seconds: float = 0.0,
        max_candles: int | None = None,
    ) -> None:
        self.strategy = strategy
        self.candles = candles
        self.execution_manager = execution_manager
        self.state = state
        self.health_monitor = health_monitor
        self.kill_switch = kill_switch
        self.persistence = persistence
        self.polling_interval_seconds = polling_interval_seconds
        self.max_candles = max_candles
        self.pipeline = CandleProcessingPipeline(
            strategy,
            execution_manager,
            state,
            health_monitor,
            kill_switch,
            persistence,
        )

    def run(self) -> None:
        """Run the local candle event loop."""
        self.run_batch()

    def run_batch(self) -> None:
        """Run the compatible candle-by-candle batch loop."""
        logger.info("Runtime event loop started candles={}", len(self.candles))
        for index, candle in enumerate(self.candles):
            if self.max_candles is not None and index >= self.max_candles:
                break
            if not self.state.active:
                break

            result = self.pipeline.process(candle, self.candles, index)
            if result.stopped:
                break
            if self.polling_interval_seconds > 0:
                sleep(self.polling_interval_seconds)
        logger.info("Runtime event loop completed")

    def run_stream_mode(self, candle_updates: Iterable[object]) -> None:
        """Process stream-driven candle-like updates while preserving the runtime path."""
        logger.info("Runtime stream mode started")
        for update in candle_updates:
            candle = update.to_candle() if hasattr(update, "to_candle") else update
            candles = CandleSeries(candle.symbol, candle.timeframe, [candle])
            self.candles = candles
            self.run_batch()
        logger.info("Runtime stream mode completed")
