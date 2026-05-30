"""Market structure detection for research-only signal intelligence."""

from __future__ import annotations

from app.data.models import Candle
from app.signal_intelligence.models import StructureState


class StructureEngine:
    """Detect HH/HL/LH/LL and structure state deterministically."""

    def detect(self, candles: list[Candle]) -> StructureState:
        if len(candles) < 4:
            raise ValueError("Structure detection requires at least four candles")
        recent = candles[-4:]
        previous_high = max(candle.high for candle in recent[:2])
        previous_low = min(candle.low for candle in recent[:2])
        current_high = max(candle.high for candle in recent[2:])
        current_low = min(candle.low for candle in recent[2:])
        higher_high = current_high > previous_high
        higher_low = current_low > previous_low
        lower_high = current_high < previous_high
        lower_low = current_low < previous_low
        if higher_high and higher_low:
            pattern = "HH/HL"
            state = "هيكل صاعد"
            contribution = 1.0
        elif lower_high and lower_low:
            pattern = "LH/LL"
            state = "هيكل هابط"
            contribution = 1.0
        elif higher_high and lower_low:
            pattern = "HH/LL"
            state = "هيكل انتقالي"
            contribution = 0.55
        else:
            pattern = "Range"
            state = "هيكل عرضي"
            contribution = 0.35
        last = recent[-1]
        return StructureState(
            timestamp=last.timestamp,
            asset=last.symbol,
            timeframe=last.timeframe,
            pattern=pattern,
            state=state,
            points={
                "previous_high": previous_high,
                "previous_low": previous_low,
                "current_high": current_high,
                "current_low": current_low,
            },
            confidence_contribution=contribution,
        )
