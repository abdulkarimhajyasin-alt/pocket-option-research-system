"""Fair value gap detection for research-only signal intelligence."""

from __future__ import annotations

from app.data.models import Candle
from app.signal_intelligence.models import FVGState


class FVGEngine:
    """Detect bullish and bearish fair value gaps."""

    def detect(self, candles: list[Candle]) -> FVGState | None:
        if len(candles) < 3:
            return None
        first, _middle, third = candles[-3:]
        current_price = candles[-1].close
        if third.low > first.high:
            gap_size = third.low - first.high
            distance = abs(current_price - third.low)
            return self._state(candles[-1], "صاعد", gap_size, distance)
        if third.high < first.low:
            gap_size = first.low - third.high
            distance = abs(current_price - third.high)
            return self._state(candles[-1], "هابط", gap_size, distance)
        return None

    def _state(
        self,
        candle: Candle,
        direction: str,
        gap_size: float,
        distance: float,
    ) -> FVGState:
        freshness = max(0.0, min(1.0, gap_size / max(distance + gap_size, 0.0000001)))
        return FVGState(
            timestamp=candle.timestamp,
            asset=candle.symbol,
            timeframe=candle.timeframe,
            direction=direction,
            gap_size=round(gap_size, 8),
            mitigated=distance < gap_size * 0.25,
            freshness_score=round(freshness, 4),
            distance_from_price=round(distance, 8),
        )
