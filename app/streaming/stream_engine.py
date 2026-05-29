"""Event-driven stream engine for validation, buffering, and monitoring."""

from loguru import logger

from app.streaming.base_stream import BaseMarketStream
from app.streaming.buffer import StreamBuffer
from app.streaming.models import MarketDataEvent
from app.streaming.monitor import StreamMonitor
from app.streaming.validator import StreamValidationResult, StreamValidator


class StreamEngine:
    """Coordinate a read-only stream with validation and rolling buffers."""

    def __init__(
        self,
        stream: BaseMarketStream,
        validator: StreamValidator | None = None,
        buffer: StreamBuffer | None = None,
        monitor: StreamMonitor | None = None,
    ) -> None:
        self.stream = stream
        self.validator = validator or StreamValidator()
        self.buffer = buffer or StreamBuffer()
        self.monitor = monitor or StreamMonitor(stream.source)

    def start(self, subscriptions: list[tuple[str, str]]) -> None:
        """Start the stream and apply subscriptions."""
        self.stream.validate_environment()
        self.stream.start()
        self.monitor.start()
        for symbol, timeframe in subscriptions:
            self.stream.subscribe(symbol, timeframe)
        logger.bind(component="streaming").info(
            "Stream engine started source={}",
            self.stream.source,
        )

    def stop(self) -> None:
        """Stop stream processing safely."""
        self.stream.stop()
        self.monitor.stop()
        logger.bind(component="streaming").info(
            "Stream engine stopped source={}",
            self.stream.source,
        )

    def poll(
        self,
        expected_timeframe: str | None = None,
    ) -> tuple[MarketDataEvent | None, StreamValidationResult | None]:
        """Fetch, validate, buffer, and monitor one event."""
        event = self.stream.next_event()
        if event is None:
            return None, None
        validation = self.validator.validate(event, expected_timeframe=expected_timeframe)
        self.monitor.record_validation(
            warnings=len(validation.warnings),
            failures=len(validation.critical_errors),
        )
        if validation.valid:
            accepted = self.buffer.add_event(event)
            if accepted:
                self.monitor.record_event(event)
            else:
                self.monitor.record_drop(duplicate=True)
        else:
            self.monitor.record_drop()
            logger.bind(component="streaming").warning(
                "Stream validation failure {}",
                validation.to_dict(),
            )
        return event, validation
