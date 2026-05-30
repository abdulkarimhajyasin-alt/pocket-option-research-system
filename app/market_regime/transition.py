"""Transition detection for market regimes."""

from __future__ import annotations

from app.market_regime.models import RegimeCandle, TransitionProfile


class TransitionDetectionEngine:
    """Detect trend and volatility transitions."""

    def evaluate(self, candles: tuple[RegimeCandle, ...]) -> TransitionProfile:
        if len(candles) < 6:
            return TransitionProfile("مرحلة انتقالية", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        midpoint = len(candles) // 2
        early = candles[:midpoint]
        late = candles[midpoint:]
        early_trend = self._trend_proxy(early)
        late_trend = self._trend_proxy(late)
        early_vol = self._vol_proxy(early)
        late_vol = self._vol_proxy(late)
        weakening = self._positive(early_trend - late_trend)
        strengthening = self._positive(late_trend - early_trend)
        ranging_to_trending = strengthening if early_trend < 35 and late_trend >= 50 else 0.0
        trending_to_ranging = weakening if early_trend >= 50 and late_trend < 35 else 0.0
        expansion = self._positive(late_vol - early_vol)
        contraction = self._positive(early_vol - late_vol)
        frequency = self._clamp(
            weakening
            + strengthening
            + ranging_to_trending
            + trending_to_ranging
            + expansion
            + contraction
        )
        state = self._state(
            weakening,
            strengthening,
            ranging_to_trending,
            trending_to_ranging,
            expansion,
            contraction,
        )
        return TransitionProfile(
            state,
            frequency,
            weakening,
            strengthening,
            ranging_to_trending,
            trending_to_ranging,
            expansion,
            contraction,
        )

    def _trend_proxy(self, candles: tuple[RegimeCandle, ...]) -> float:
        closes = [candle.close for candle in candles]
        net = abs(closes[-1] - closes[0])
        path = sum(abs(closes[index] - closes[index - 1]) for index in range(1, len(closes)))
        return self._clamp(net / max(path, 0.00001) * 100)

    def _vol_proxy(self, candles: tuple[RegimeCandle, ...]) -> float:
        first = max(candles[0].close, 0.00001)
        average_range = sum(candle.range for candle in candles) / len(candles)
        return self._clamp(average_range / first * 100000)

    def _state(
        self,
        weakening: float,
        strengthening: float,
        r2t: float,
        t2r: float,
        expansion: float,
        contraction: float,
    ) -> str:
        values = {
            "ضعف الاتجاه": weakening,
            "تقوية الاتجاه": strengthening,
            "من عرضي إلى اتجاه": r2t,
            "من اتجاه إلى عرضي": t2r,
            "توسع التقلب": expansion,
            "انكماش التقلب": contraction,
        }
        state, value = max(values.items(), key=lambda item: item[1])
        return state if value >= 10 else "مستقر"

    def _positive(self, value: float) -> float:
        return self._clamp(max(0.0, value))

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(100.0, float(value))), 2)
