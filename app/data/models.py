"""Market data domain models."""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Candle:
    """Represents one normalized OHLCV market data candle."""

    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None

    def __post_init__(self) -> None:
        """Validate candle consistency after initialization."""
        if not self.symbol.strip():
            raise ValueError("Candle symbol is required")
        if not self.timeframe.strip():
            raise ValueError("Candle timeframe is required")
        if self.timestamp.tzinfo is None:
            raise ValueError("Candle timestamp must be timezone-aware")
        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("Candle prices must be positive")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("Candle high must be greater than or equal to OHLC prices")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("Candle low must be less than or equal to OHLC prices")
        if self.volume is not None and self.volume < 0:
            raise ValueError("Candle volume cannot be negative")

    @property
    def is_bullish(self) -> bool:
        """Return True when the candle closes above its open."""
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """Return True when the candle closes below its open."""
        return self.close < self.open

    @property
    def is_neutral(self) -> bool:
        """Return True when the candle close equals its open."""
        return self.close == self.open

    @property
    def typical_price(self) -> float:
        """Return the average of high, low, and close."""
        return (self.high + self.low + self.close) / 3


class CandleSeries(Sequence[Candle]):
    """Immutable-style ordered container for normalized candles."""

    def __init__(self, symbol: str, timeframe: str, candles: Sequence[Candle]) -> None:
        if not symbol.strip():
            raise ValueError("CandleSeries symbol is required")
        if not timeframe.strip():
            raise ValueError("CandleSeries timeframe is required")

        self.symbol = symbol
        self.timeframe = timeframe
        self._candles = tuple(candles)
        self._validate()

    def __getitem__(self, index: int | slice) -> Candle | tuple[Candle, ...]:
        """Return one candle or a slice of candles."""
        return self._candles[index]

    def __len__(self) -> int:
        """Return the number of candles in the series."""
        return len(self._candles)

    def __iter__(self) -> Iterator[Candle]:
        """Iterate through candles in chronological order."""
        return iter(self._candles)

    def _validate(self) -> None:
        previous_timestamp: datetime | None = None
        seen_timestamps: set[datetime] = set()

        for candle in self._candles:
            if candle.symbol != self.symbol:
                raise ValueError("All candles must share the series symbol")
            if candle.timeframe != self.timeframe:
                raise ValueError("All candles must share the series timeframe")
            if candle.timestamp in seen_timestamps:
                raise ValueError("CandleSeries cannot contain duplicate timestamps")
            if previous_timestamp is not None and candle.timestamp < previous_timestamp:
                raise ValueError("CandleSeries must be sorted by timestamp")

            seen_timestamps.add(candle.timestamp)
            previous_timestamp = candle.timestamp

    @property
    def first(self) -> Candle | None:
        """Return the first candle, if available."""
        return self._candles[0] if self._candles else None

    @property
    def last(self) -> Candle | None:
        """Return the last candle, if available."""
        return self._candles[-1] if self._candles else None

    def history_until(self, index: int) -> tuple[Candle, ...]:
        """Return candles up to and including the requested index."""
        return self._candles[: index + 1]
