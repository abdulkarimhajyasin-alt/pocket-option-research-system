"""Streaming runtime integration for read-only market data flow."""

from __future__ import annotations

from loguru import logger

from app.data.models import CandleSeries
from app.execution.execution_manager import ExecutionManager
from app.runtime.health import HealthMonitor
from app.runtime.kill_switch import KillSwitch
from app.runtime.pipeline import CandleProcessingPipeline
from app.runtime.runtime_state import RuntimeState
from app.storage.persistence import PersistenceService
from app.strategies.base_strategy import BaseStrategy
from app.streaming.base_stream import BaseMarketStream
from app.streaming.buffer import StreamBuffer
from app.streaming.models import CandleUpdate, StreamEventType
from app.streaming.stream_engine import StreamEngine


class StreamingRuntime:
    """Feed closed stream candles into the existing strategy/risk/paper execution path."""

    def __init__(
        self,
        stream: BaseMarketStream,
        strategy: BaseStrategy | None = None,
        execution_manager: ExecutionManager | None = None,
        state: RuntimeState | None = None,
        health_monitor: HealthMonitor | None = None,
        kill_switch: KillSwitch | None = None,
        persistence: PersistenceService | None = None,
        engine: StreamEngine | None = None,
    ) -> None:
        self.stream = stream
        self.strategy = strategy
        self.execution_manager = execution_manager
        self.state = state
        self.health_monitor = health_monitor
        self.kill_switch = kill_switch
        self.persistence = persistence
        self.engine = engine or StreamEngine(stream)
        self.closed_candles: list[CandleUpdate] = []
        self.pipeline = (
            CandleProcessingPipeline(
                strategy,
                execution_manager,
                state,
                health_monitor,
                kill_switch,
                persistence,
            )
            if all([strategy, execution_manager, state, health_monitor, kill_switch])
            else None
        )

    def start(self, subscriptions: list[tuple[str, str]]) -> None:
        """Start stream services and subscriptions."""
        self.engine.start(subscriptions)
        if self.persistence:
            self.persistence.persist_stream_event(
                "stream.start",
                self.stream.source,
                {"subscriptions": subscriptions},
            )

    def stop(self) -> None:
        """Shutdown stream services safely."""
        self.engine.stop()
        if self.persistence:
            self.persistence.persist_stream_health(
                self.stream.source,
                self.stream.get_health().to_dict(),
            )

    def run(
        self,
        max_events: int = 25,
        expected_timeframe: str | None = None,
    ) -> dict[str, object]:
        """Consume events and process closed candles through existing runtime services."""
        for _ in range(max_events):
            event, validation = self.engine.poll(expected_timeframe=expected_timeframe)
            if event is None:
                break
            if self.persistence and validation and not validation.valid:
                self.persistence.persist_stream_validation_failure(
                    self.stream.source,
                    validation.to_dict(),
                )
            if (
                event.event_type == StreamEventType.CANDLE
                and event.candle
                and event.candle.is_closed
            ):
                self.closed_candles.append(event.candle)
                self._process_closed_candle(event.candle, self.engine.buffer)
        return self.diagnostics()

    def diagnostics(self) -> dict[str, object]:
        """Return stream runtime diagnostics."""
        return {
            "stream": self.stream.get_health().to_dict(),
            "monitor": self.engine.monitor.snapshot().to_dict(),
            "buffered_events": len(self.engine.buffer.events),
            "buffered_candles": len(self.engine.buffer.candles),
            "closed_candles": len(self.closed_candles),
        }

    def _process_closed_candle(self, update: CandleUpdate, buffer: StreamBuffer) -> None:
        runtime_ready = all(
            [
                self.strategy,
                self.execution_manager,
                self.state,
                self.health_monitor,
                self.kill_switch,
            ]
        )
        if not runtime_ready:
            return
        candle = update.to_candle()
        history = tuple(
            item.to_candle() for item in buffer.candle_history(update.symbol, update.timeframe)
        )
        series = CandleSeries(update.symbol, update.timeframe, history)
        index = max(0, len(series) - 1)
        if self.pipeline is None:
            return
        self.pipeline.process(candle, series, index, metadata={"streaming": True})
        logger.bind(component="streaming").info("Processed stream candle {}", update.to_dict())
