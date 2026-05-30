"""Configurable confluence scoring."""

from __future__ import annotations

from dataclasses import dataclass

from app.confluence.models import FactorScore


@dataclass(frozen=True)
class ConfluenceWeights:
    """Default factor weights for unified research confluence."""

    signal: float = 15.0
    performance: float = 20.0
    opportunity: float = 20.0
    timeframe: float = 20.0
    session: float = 10.0
    liquidity: float = 15.0

    def to_dict(self) -> dict[str, float]:
        return {
            "عامل الإشارة": self.signal,
            "عامل الأداء": self.performance,
            "عامل الفرصة": self.opportunity,
            "عامل الأطر الزمنية": self.timeframe,
            "عامل الجلسة": self.session,
            "عامل السيولة": self.liquidity,
        }


class ConfluenceScoringEngine:
    """Combine factor scores into one bounded research-quality metric."""

    def __init__(self, weights: ConfluenceWeights | None = None) -> None:
        self.weights = weights or ConfluenceWeights()

    def score(self, factors: tuple[FactorScore, ...]) -> float:
        weights = self.weights.to_dict()
        total = sum(weights.get(factor.name, 0.0) for factor in factors)
        if total <= 0:
            return 0.0
        raw = sum(factor.score * weights.get(factor.name, 0.0) for factor in factors)
        return round(max(0.0, min(100.0, raw / total)), 2)


class ResearchReadinessEngine:
    """Classify research readiness without making trading recommendations."""

    def evaluate(self, score: float, factors: tuple[FactorScore, ...]) -> str:
        minimum = min((factor.score for factor in factors), default=0.0)
        if score >= 80 and minimum >= 55:
            return "جاهزة للأبحاث المتقدمة"
        if score >= 55:
            return "تحتاج تحسين"
        return "غير مؤهلة"
