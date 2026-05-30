"""Liquidity sweep detection for research-only signal intelligence."""

from __future__ import annotations

from app.data.models import Candle
from app.signal_intelligence.models import LiquidityState


class LiquidityEngine:
    """Detect local highs, lows, and sweep confirmation."""

    def detect(self, candles: list[Candle]) -> LiquidityState:
        if len(candles) < 5:
            raise ValueError("Liquidity detection requires at least five candles")
        prior = candles[-5:-1]
        current = candles[-1]
        local_high = max(candle.high for candle in prior)
        local_low = min(candle.low for candle in prior)
        swept_high = current.high > local_high and current.close < local_high
        swept_low = current.low < local_low and current.close > local_low
        if swept_high:
            direction = "سحب سيولة علوية"
        elif swept_low:
            direction = "سحب سيولة سفلية"
        else:
            direction = "لا يوجد سحب"
        return LiquidityState(
            timestamp=current.timestamp,
            asset=current.symbol,
            timeframe=current.timeframe,
            local_high=local_high,
            local_low=local_low,
            sweep_direction=direction,
            sweep_confirmed=swept_high or swept_low,
            confidence_contribution=1.0 if swept_high or swept_low else 0.25,
        )
