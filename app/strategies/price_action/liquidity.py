"""Liquidity sweep research detection."""

from dataclasses import dataclass

from app.data.models import Candle
from app.strategies.research.models import EvidenceDirection


@dataclass(frozen=True)
class LiquiditySweep:
    """Simple sweep of recent high or low followed by rejection."""

    direction: EvidenceDirection
    swept_level: float
    index: int
    strength: float
    detected: bool = True


def detect_liquidity_sweep(
    candles: tuple[Candle, ...],
    lookback: int = 5,
    tolerance: float = 0.0,
) -> LiquiditySweep | None:
    """Detect a sweep of recent liquidity on the latest candle."""
    if len(candles) < lookback + 1:
        return None
    current = candles[-1]
    prior = candles[-lookback - 1 : -1]
    prior_high = max(candle.high for candle in prior)
    prior_low = min(candle.low for candle in prior)
    candle_range = max(current.high - current.low, 0.0000001)
    if current.high > prior_high + tolerance and current.close < prior_high:
        strength = min(1.0, (current.high - prior_high) / candle_range)
        return LiquiditySweep(EvidenceDirection.BEARISH, prior_high, len(candles) - 1, strength)
    if current.low < prior_low - tolerance and current.close > prior_low:
        strength = min(1.0, (prior_low - current.low) / candle_range)
        return LiquiditySweep(EvidenceDirection.BULLISH, prior_low, len(candles) - 1, strength)
    return None
