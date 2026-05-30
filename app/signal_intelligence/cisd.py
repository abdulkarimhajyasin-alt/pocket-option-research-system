"""CISD detection for research-only signal intelligence."""

from __future__ import annotations

from app.data.models import Candle
from app.signal_intelligence.models import CISDState


class CISDEngine:
    """Detect bullish and bearish change in state delivery."""

    def detect(self, candles: list[Candle]) -> CISDState:
        if len(candles) < 3:
            raise ValueError("CISD detection requires at least three candles")
        previous = candles[-2]
        current = candles[-1]
        body = abs(current.close - current.open)
        candle_range = max(current.high - current.low, 0.0000001)
        body_ratio = body / candle_range
        bullish = current.close > previous.high and current.close > current.open
        bearish = current.close < previous.low and current.close < current.open
        validated = (bullish or bearish) and body_ratio >= 0.35
        direction = "صاعد" if bullish else "هابط" if bearish else "محايد"
        explanation = (
            "إغلاق صاعد تجاوز القمة السابقة"
            if bullish
            else "إغلاق هابط كسر القاع السابق"
            if bearish
            else "لا يوجد تغير حالة مؤكد"
        )
        return CISDState(
            timestamp=current.timestamp,
            asset=current.symbol,
            timeframe=current.timeframe,
            direction=direction,
            validated=validated,
            confidence_contribution=1.0 if validated else 0.25,
            explanation=explanation,
        )
