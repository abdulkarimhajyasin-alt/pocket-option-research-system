"""Tick-to-candle aggregation pipeline for streaming market data."""

from dataclasses import replace
from datetime import datetime, timedelta

from loguru import logger

from app.streaming.models import CandleUpdate, MarketTick, normalize_timeframe


def timeframe_seconds(timeframe: str) -> int:
    """Return supported timeframe duration in seconds."""
    normalized = normalize_timeframe(timeframe)
    return 60 if normalized == "1m" else 300


class CandleAggregator:
    """Aggregate read-only ticks into M1/M5 candle updates."""

    def __init__(
        self,
        timeframe: str,
        source: str = "aggregator",
        allow_late_ticks: bool = False,
    ) -> None:
        self.timeframe = normalize_timeframe(timeframe)
        self.source = source
        self.allow_late_ticks = allow_late_ticks
        self._open_candles: dict[str, CandleUpdate] = {}
        self.late_ticks = 0
        self.missing_tick_gaps = 0

    def update(self, tick: MarketTick) -> list[CandleUpdate]:
        """Apply a tick and return partial/closed candle updates."""
        bucket = self._bucket_start(tick.timestamp)
        current = self._open_candles.get(tick.symbol)
        emitted: list[CandleUpdate] = []

        if current is not None and bucket < current.timestamp:
            self.late_ticks += 1
            logger.bind(component="streaming").warning(
                "Late tick ignored symbol={} tick={} candle={}",
                tick.symbol,
                tick.timestamp,
                current.timestamp,
            )
            return [] if not self.allow_late_ticks else [current]

        if current is None:
            current = self._new_candle(tick, bucket, is_closed=False)
        elif bucket > current.timestamp:
            emitted.append(replace(current, is_closed=True, sequence=tick.sequence))
            expected = current.timestamp + timedelta(seconds=timeframe_seconds(self.timeframe))
            if bucket > expected:
                self.missing_tick_gaps += 1
            current = self._new_candle(tick, bucket, is_closed=False)
        else:
            current = replace(
                current,
                high=max(current.high, tick.price),
                low=min(current.low, tick.price),
                close=tick.price,
                latency_ms=tick.latency_ms,
                sequence=tick.sequence,
            )

        self._open_candles[tick.symbol] = current
        emitted.append(current)
        logger.bind(component="streaming").debug(
            "Candle aggregation symbol={} timeframe={} closed={}",
            current.symbol,
            current.timeframe,
            current.is_closed,
        )
        return emitted

    def flush(self) -> list[CandleUpdate]:
        """Close all currently open candles."""
        closed = [replace(candle, is_closed=True) for candle in self._open_candles.values()]
        self._open_candles.clear()
        return closed

    def _new_candle(self, tick: MarketTick, timestamp: datetime, is_closed: bool) -> CandleUpdate:
        return CandleUpdate(
            symbol=tick.symbol,
            timeframe=self.timeframe,
            timestamp=timestamp,
            open=tick.price,
            high=tick.price,
            low=tick.price,
            close=tick.price,
            source=self.source,
            volume=1.0,
            is_closed=is_closed,
            latency_ms=tick.latency_ms,
            sequence=tick.sequence,
        )

    def _bucket_start(self, timestamp: datetime) -> datetime:
        seconds = timeframe_seconds(self.timeframe)
        epoch = int(timestamp.timestamp())
        return datetime.fromtimestamp(epoch - (epoch % seconds), tz=timestamp.tzinfo)
