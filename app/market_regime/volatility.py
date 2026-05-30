"""Volatility analysis for market regime detection."""

from __future__ import annotations

from app.market_regime.models import RegimeCandle, VolatilityProfile


class VolatilityEngine:
    """Measure candle expansion, movement, session volatility, and stability."""

    def evaluate(self, candles: tuple[RegimeCandle, ...]) -> VolatilityProfile:
        if not candles:
            return VolatilityProfile(0.0, "منخفض", 0.0, 0.0, 0.0, 0.0, 0.0)
        ranges = [candle.range for candle in candles]
        bodies = [candle.body for candle in candles]
        average_range = self._average(ranges)
        average_body = self._average(bodies)
        base = max(candles[0].close, 0.00001)
        movement = self._clamp(average_range / base * 100000)
        expansion = self._clamp(average_body / max(average_range, 0.00001) * 100)
        session_volatility = self._clamp(max(ranges) / base * 100000)
        stability = self._clamp(100 - self._relative_spread(ranges) * 100)
        trend = self._volatility_trend(ranges)
        score = self._clamp(
            movement * 0.3
            + expansion * 0.2
            + session_volatility * 0.25
            + stability * 0.15
            + trend * 0.1
        )
        return VolatilityProfile(
            score,
            self._category(score),
            expansion,
            movement,
            session_volatility,
            stability,
            trend,
        )

    def _volatility_trend(self, ranges: list[float]) -> float:
        if len(ranges) < 4:
            return 0.0
        midpoint = len(ranges) // 2
        early = self._average(ranges[:midpoint])
        late = self._average(ranges[midpoint:])
        if early <= 0:
            return 50.0
        return self._clamp((late / early) * 50)

    def _relative_spread(self, values: list[float]) -> float:
        average = self._average(values)
        if average <= 0:
            return 0.0
        return (max(values) - min(values)) / average

    def _category(self, score: float) -> str:
        if score >= 85:
            return "مرتفع جدا"
        if score >= 65:
            return "مرتفع"
        if score >= 40:
            return "متوسط"
        return "منخفض"

    def _average(self, values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(100.0, float(value))), 2)
