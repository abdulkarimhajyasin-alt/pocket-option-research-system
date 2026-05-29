"""Rolling buffers for stream events and candles."""

from collections import deque

from app.streaming.models import CandleUpdate, MarketDataEvent, StreamEventType


class StreamBuffer:
    """Maintain deduplicated rolling event and candle context."""

    def __init__(self, max_events: int = 500, max_candles: int = 200) -> None:
        if max_events <= 0 or max_candles <= 0:
            raise ValueError("Buffer sizes must be positive")
        self.max_events = max_events
        self.max_candles = max_candles
        self.events: deque[MarketDataEvent] = deque(maxlen=max_events)
        self.candles: deque[CandleUpdate] = deque(maxlen=max_candles)
        self._event_keys: set[tuple[str, int, str]] = set()
        self.duplicates = 0

    def add_event(self, event: MarketDataEvent) -> bool:
        """Add an event, returning False when it is a duplicate."""
        key = (event.source, event.sequence, event.event_id)
        if key in self._event_keys:
            self.duplicates += 1
            return False
        self._event_keys.add(key)
        ordered = sorted([*self.events, event], key=lambda item: (item.timestamp, item.sequence))
        self.events.clear()
        self.events.extend(ordered[-self.max_events :])
        self._event_keys = {(item.source, item.sequence, item.event_id) for item in self.events}
        if event.event_type == StreamEventType.CANDLE and event.candle is not None:
            self.add_candle(event.candle)
        return True

    def add_candle(self, candle: CandleUpdate) -> None:
        """Add or replace a candle update in timestamp order."""
        existing = [
            item
            for item in self.candles
            if not (
                item.symbol == candle.symbol
                and item.timeframe == candle.timeframe
                and item.timestamp == candle.timestamp
            )
        ]
        ordered = sorted([*existing, candle], key=lambda item: (item.timestamp, item.sequence))
        self.candles.clear()
        self.candles.extend(ordered[-self.max_candles :])

    def latest_candle(self, symbol: str, timeframe: str) -> CandleUpdate | None:
        """Return latest candle context for a strategy."""
        for candle in reversed(self.candles):
            if candle.symbol == symbol.upper() and candle.timeframe == timeframe:
                return candle
        return None

    def candle_history(self, symbol: str, timeframe: str) -> tuple[CandleUpdate, ...]:
        """Return rolling candle history for a symbol/timeframe."""
        return tuple(
            candle
            for candle in self.candles
            if candle.symbol == symbol.upper() and candle.timeframe == timeframe
        )
