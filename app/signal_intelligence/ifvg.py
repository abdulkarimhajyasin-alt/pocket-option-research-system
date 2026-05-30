"""Inverse FVG detection for research-only signal intelligence."""

from __future__ import annotations

from app.data.models import Candle
from app.signal_intelligence.models import FVGState, IFVGState


class IFVGEngine:
    """Detect inverse FVG confirmation from an origin FVG."""

    def detect(self, candles: list[Candle], fvg: FVGState | None) -> IFVGState | None:
        if fvg is None or not candles:
            return None
        current = candles[-1]
        inverted = (
            fvg.direction == "صاعد"
            and current.close < current.open
            and fvg.mitigated
        ) or (
            fvg.direction == "هابط"
            and current.close > current.open
            and fvg.mitigated
        )
        return IFVGState(
            timestamp=current.timestamp,
            asset=current.symbol,
            timeframe=current.timeframe,
            origin_direction=fvg.direction,
            inverted=inverted,
            confirmed=inverted and abs(current.close - current.open) > 0,
            confidence_contribution=1.0 if inverted else 0.2,
        )
