"""Market regime analytics."""

from __future__ import annotations

from typing import Any

from app.market_regime.models import MarketRegimeRun


class MarketRegimeAnalytics:
    """Compute regime distributions and dashboard analytics."""

    def summarize(self, result: MarketRegimeRun) -> dict[str, Any]:
        regime = result.regime
        compatibility = result.compatibility
        transition = regime.transition
        return {
            "summary": {
                "regime_state": regime.regime_state,
                "regime_score": regime.regime_score,
                "volatility_score": regime.volatility.score,
                "trend_strength": regime.trend.score,
                "compatibility_score": compatibility.score,
                "compatibility_category": compatibility.category,
                "stability_score": regime.stability_score,
                "quality_score": regime.quality_score,
                "research_only": True,
            },
            "regime_distribution": {regime.regime_state: regime.regime_score},
            "volatility_distribution": {
                regime.volatility.category: regime.volatility.score,
                "تمدد الشموع": regime.volatility.candle_expansion,
                "متوسط الحركة": regime.volatility.average_movement,
                "استقرار التقلب": regime.volatility.volatility_stability,
            },
            "trend_distribution": {
                regime.trend.direction: regime.trend.score,
                "اتساق الاتجاه": regime.trend.directional_consistency,
                "استمرار الاتجاه": regime.trend.trend_persistence,
                "ثقة الاتجاه": regime.trend.trend_confidence,
            },
            "transition_frequency": {
                transition.state: transition.frequency,
                "ضعف الاتجاه": transition.trend_weakening,
                "تقوية الاتجاه": transition.trend_strengthening,
                "توسع التقلب": transition.volatility_expansion,
                "انكماش التقلب": transition.volatility_contraction,
            },
            "compatibility_analysis": {
                "الإشارات": compatibility.signal_score,
                "الفرص": compatibility.opportunity_score,
                "الأطر الزمنية": compatibility.timeframe_score,
                "التوافق": compatibility.confluence_score,
                "ذاكرة الأنماط": compatibility.pattern_score,
            },
            "regime_quality": result.pattern_analysis.distribution,
            "regime_stability": {
                regime.regime_state: regime.stability_score,
                "الجودة": regime.quality_score,
                "التوافق": compatibility.score,
            },
            "historical_performance": result.pattern_analysis.distribution,
            "latest": result.to_dict(),
        }
