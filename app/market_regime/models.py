"""Typed models for market regime research."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RegimeCandle:
    """Minimal local candle used for regime analysis."""

    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    @property
    def body(self) -> float:
        return abs(self.close - self.open)

    @property
    def range(self) -> float:
        return max(0.0, self.high - self.low)

    @property
    def direction(self) -> int:
        if self.close > self.open:
            return 1
        if self.close < self.open:
            return -1
        return 0


@dataclass(frozen=True)
class VolatilityProfile:
    """Volatility score and supporting components."""

    score: float
    category: str
    candle_expansion: float
    average_movement: float
    session_volatility: float
    volatility_stability: float
    volatility_trend: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "category": self.category,
            "candle_expansion": self.candle_expansion,
            "average_movement": self.average_movement,
            "session_volatility": self.session_volatility,
            "volatility_stability": self.volatility_stability,
            "volatility_trend": self.volatility_trend,
        }


@dataclass(frozen=True)
class TrendProfile:
    """Trend strength score and supporting components."""

    score: float
    direction: str
    structure_alignment: float
    trend_persistence: float
    directional_consistency: float
    trend_confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "direction": self.direction,
            "structure_alignment": self.structure_alignment,
            "trend_persistence": self.trend_persistence,
            "directional_consistency": self.directional_consistency,
            "trend_confidence": self.trend_confidence,
        }


@dataclass(frozen=True)
class TransitionProfile:
    """Transition state and transition components."""

    state: str
    frequency: float
    trend_weakening: float
    trend_strengthening: float
    ranging_to_trending: float
    trending_to_ranging: float
    volatility_expansion: float
    volatility_contraction: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "frequency": self.frequency,
            "trend_weakening": self.trend_weakening,
            "trend_strengthening": self.trend_strengthening,
            "ranging_to_trending": self.ranging_to_trending,
            "trending_to_ranging": self.trending_to_ranging,
            "volatility_expansion": self.volatility_expansion,
            "volatility_contraction": self.volatility_contraction,
        }


@dataclass(frozen=True)
class MarketRegimeResult:
    """Current market regime classification."""

    regime_state: str
    regime_score: float
    volatility: VolatilityProfile
    trend: TrendProfile
    transition: TransitionProfile
    stability_score: float
    quality_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "regime_state": self.regime_state,
            "regime_score": self.regime_score,
            "volatility": self.volatility.to_dict(),
            "trend": self.trend.to_dict(),
            "transition": self.transition.to_dict(),
            "stability_score": self.stability_score,
            "quality_score": self.quality_score,
            "research_only": True,
        }


@dataclass(frozen=True)
class CompatibilityResult:
    """Compatibility between regime and research layers."""

    score: float
    category: str
    signal_score: float
    opportunity_score: float
    timeframe_score: float
    confluence_score: float
    pattern_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "category": self.category,
            "signal_score": self.signal_score,
            "opportunity_score": self.opportunity_score,
            "timeframe_score": self.timeframe_score,
            "confluence_score": self.confluence_score,
            "pattern_score": self.pattern_score,
            "research_only": True,
            "not_recommendation": True,
        }


@dataclass(frozen=True)
class PatternRegimeAnalysis:
    """Historical pattern quality by regime."""

    best_signals: str
    best_opportunities: str
    strongest_confluence: str
    highest_stability: str
    highest_quality_patterns: str
    distribution: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "best_signals": self.best_signals,
            "best_opportunities": self.best_opportunities,
            "strongest_confluence": self.strongest_confluence,
            "highest_stability": self.highest_stability,
            "highest_quality_patterns": self.highest_quality_patterns,
            "distribution": self.distribution,
        }


@dataclass(frozen=True)
class MarketRegimeRun:
    """Full market regime run result."""

    timestamp: datetime
    regime: MarketRegimeResult
    compatibility: CompatibilityResult
    pattern_analysis: PatternRegimeAnalysis
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "regime": self.regime.to_dict(),
            "compatibility": self.compatibility.to_dict(),
            "pattern_analysis": self.pattern_analysis.to_dict(),
            "metadata": self.metadata,
            "research_only": True,
            "not_execution": True,
            "not_broker_control": True,
            "not_account_interaction": True,
            "not_investment_advice": True,
            "not_profitability_claim": True,
        }
