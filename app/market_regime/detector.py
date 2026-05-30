"""Market regime detector and local candle loader."""

from __future__ import annotations

import csv
from pathlib import Path

from app.market_regime.models import (
    MarketRegimeResult,
    RegimeCandle,
    TransitionProfile,
    TrendProfile,
    VolatilityProfile,
)


class MarketRegimeDetector:
    """Classify the current research market environment."""

    def classify(
        self,
        volatility: VolatilityProfile,
        trend: TrendProfile,
        transition: TransitionProfile,
    ) -> MarketRegimeResult:
        state = self._state(volatility, trend, transition)
        stability = self._clamp(
            volatility.volatility_stability * 0.4
            + trend.directional_consistency * 0.35
            + (100 - transition.frequency) * 0.25
        )
        quality = self._clamp(
            trend.score * 0.35
            + volatility.score * 0.25
            + stability * 0.25
            + (100 - transition.frequency) * 0.15
        )
        score = self._clamp(
            quality * 0.45 + stability * 0.3 + trend.score * 0.15 + volatility.score * 0.1
        )
        return MarketRegimeResult(
            state,
            score,
            volatility,
            trend,
            transition,
            stability,
            quality,
        )

    def _state(
        self,
        volatility: VolatilityProfile,
        trend: TrendProfile,
        transition: TransitionProfile,
    ) -> str:
        if transition.frequency >= 55:
            return "مرحلة انتقالية"
        if trend.score >= 70 and trend.direction == "صاعد":
            return "اتجاه صاعد قوي"
        if trend.score >= 70 and trend.direction == "هابط":
            return "اتجاه هابط قوي"
        if volatility.score >= 75:
            return "تقلب مرتفع"
        if volatility.score <= 30:
            return "تقلب منخفض"
        if trend.score >= 45:
            return "اتجاه متوسط"
        if abs(trend.structure_alignment - volatility.score) >= 45:
            return "حالة متضاربة"
        return "سوق عرضي"

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(100.0, float(value))), 2)


class RegimeCandleLoader:
    """Load local historical candles without broker connectivity."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def load(self, relative_path: str = "data/sample_eurusd_m1.csv") -> tuple[RegimeCandle, ...]:
        path = self.project_root / relative_path
        if not path.exists():
            return ()
        rows = []
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                rows.append(
                    RegimeCandle(
                        timestamp=str(row.get("timestamp", "")),
                        open=self._float(row.get("open")),
                        high=self._float(row.get("high")),
                        low=self._float(row.get("low")),
                        close=self._float(row.get("close")),
                        volume=self._float(row.get("volume")),
                    )
                )
        return tuple(rows)

    def _float(self, value: object) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
