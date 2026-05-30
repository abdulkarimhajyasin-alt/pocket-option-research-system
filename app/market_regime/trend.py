"""Trend strength analysis for market regime detection."""

from __future__ import annotations

from app.market_regime.models import RegimeCandle, TrendProfile


class TrendStrengthEngine:
    """Evaluate structure alignment, persistence, consistency, and confidence."""

    def evaluate(self, candles: tuple[RegimeCandle, ...]) -> TrendProfile:
        if len(candles) < 2:
            return TrendProfile(0.0, "محايد", 0.0, 0.0, 0.0, 0.0)
        closes = [candle.close for candle in candles]
        directions = [candle.direction for candle in candles if candle.direction != 0]
        net_change = closes[-1] - closes[0]
        total_path = sum(abs(closes[index] - closes[index - 1]) for index in range(1, len(closes)))
        structure = self._clamp(abs(net_change) / max(total_path, 0.00001) * 100)
        persistence = self._persistence(closes)
        consistency = self._directional_consistency(directions, net_change)
        confidence = self._clamp((structure + persistence + consistency) / 3)
        score = self._clamp(
            structure * 0.3
            + persistence * 0.25
            + consistency * 0.25
            + confidence * 0.2
        )
        return TrendProfile(
            score,
            "صاعد" if net_change > 0 else "هابط" if net_change < 0 else "محايد",
            structure,
            persistence,
            consistency,
            confidence,
        )

    def _persistence(self, closes: list[float]) -> float:
        if len(closes) < 3:
            return 0.0
        slopes = [
            1 if closes[index] > closes[index - 1] else -1
            for index in range(1, len(closes))
            if closes[index] != closes[index - 1]
        ]
        if not slopes:
            return 0.0
        dominant = max(slopes.count(1), slopes.count(-1))
        return self._clamp(dominant / len(slopes) * 100)

    def _directional_consistency(
        self,
        directions: list[int],
        net_change: float,
    ) -> float:
        if not directions:
            return 0.0
        dominant = 1 if net_change >= 0 else -1
        matched = sum(1 for item in directions if item == dominant)
        return self._clamp(matched / len(directions) * 100)

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(100.0, float(value))), 2)
