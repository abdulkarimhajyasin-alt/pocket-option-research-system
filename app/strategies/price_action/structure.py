"""Market structure research utilities."""

from dataclasses import dataclass
from enum import StrEnum

from app.data.models import Candle


class StructureDirection(StrEnum):
    """Basic market structure direction."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class SwingPoint:
    """Detected swing high or swing low."""

    index: int
    timestamp: object
    price: float
    kind: str


def detect_swing_highs(candles: tuple[Candle, ...], lookback: int = 2) -> tuple[SwingPoint, ...]:
    """Detect local swing highs using symmetric lookback."""
    swings: list[SwingPoint] = []
    for index in range(lookback, len(candles) - lookback):
        candle = candles[index]
        neighbors = candles[index - lookback : index] + candles[index + 1 : index + lookback + 1]
        if all(candle.high > other.high for other in neighbors):
            swings.append(SwingPoint(index, candle.timestamp, candle.high, "swing_high"))
    return tuple(swings)


def detect_swing_lows(candles: tuple[Candle, ...], lookback: int = 2) -> tuple[SwingPoint, ...]:
    """Detect local swing lows using symmetric lookback."""
    swings: list[SwingPoint] = []
    for index in range(lookback, len(candles) - lookback):
        candle = candles[index]
        neighbors = candles[index - lookback : index] + candles[index + 1 : index + lookback + 1]
        if all(candle.low < other.low for other in neighbors):
            swings.append(SwingPoint(index, candle.timestamp, candle.low, "swing_low"))
    return tuple(swings)


def market_structure_direction(
    candles: tuple[Candle, ...],
    lookback: int = 2,
) -> StructureDirection:
    """Estimate direction from recent swing progression and closes."""
    if len(candles) < lookback * 2 + 3:
        return StructureDirection.NEUTRAL
    highs = detect_swing_highs(candles, lookback)
    lows = detect_swing_lows(candles, lookback)
    if len(highs) >= 2 and len(lows) >= 2:
        higher_high = highs[-1].price > highs[-2].price
        higher_low = lows[-1].price > lows[-2].price
        lower_high = highs[-1].price < highs[-2].price
        lower_low = lows[-1].price < lows[-2].price
        if higher_high and higher_low:
            return StructureDirection.BULLISH
        if lower_high and lower_low:
            return StructureDirection.BEARISH
    if candles[-1].close > candles[-lookback - 1].close:
        return StructureDirection.BULLISH
    if candles[-1].close < candles[-lookback - 1].close:
        return StructureDirection.BEARISH
    return StructureDirection.NEUTRAL
