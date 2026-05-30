"""Regime compatibility and pattern-regime analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.market_regime.models import CompatibilityResult, MarketRegimeResult
from app.market_regime.models import PatternRegimeAnalysis


class RegimeCompatibilityEngine:
    """Evaluate compatibility between regime and research layers."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def evaluate(self, regime: MarketRegimeResult) -> CompatibilityResult:
        signal = self._score("reports/signals/signal_summary.json", "summary")
        opportunity = self._score("reports/opportunities/opportunity_summary.json", "summary")
        timeframe = self._score("reports/multi_timeframe/confirmation_summary.json", "summary")
        confluence = self._score("reports/confluence/confluence_summary.json", "summary")
        pattern = self._score("reports/pattern_memory/pattern_summary.json", "summary")
        regime_bias = self._regime_bias(regime)
        score = self._clamp(
            (signal + opportunity + timeframe + confluence + pattern) / 5 * 0.7
            + regime_bias * 0.3
        )
        return CompatibilityResult(
            score,
            self._category(score),
            signal,
            opportunity,
            timeframe,
            confluence,
            pattern,
        )

    def _score(self, relative_path: str, section: str) -> float:
        payload = self._load(relative_path)
        if section and isinstance(payload.get(section), dict):
            payload = payload[section]
        for key in (
            "average_confidence",
            "average_quality",
            "average_score",
            "average_confluence",
            "average_confirmation",
            "reliability_score",
            "health_score",
            "readiness_score",
        ):
            if key in payload:
                return self._clamp(payload[key])
        return 60.0

    def _load(self, relative_path: str) -> dict[str, Any]:
        path = self.project_root / relative_path
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}

    def _regime_bias(self, regime: MarketRegimeResult) -> float:
        if "قوي" in regime.regime_state:
            return max(regime.trend.score, regime.quality_score)
        if "عرضي" in regime.regime_state:
            return regime.stability_score
        if "متضاربة" in regime.regime_state:
            return 35.0
        if "انتقالية" in regime.regime_state:
            return 45.0
        return regime.regime_score

    def _category(self, score: float) -> str:
        if score >= 85:
            return "متوافق جدا"
        if score >= 70:
            return "متوافق"
        if score >= 55:
            return "محايد"
        if score >= 40:
            return "ضعيف"
        return "غير متوافق"

    def _clamp(self, value: object) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = 0.0
        return round(max(0.0, min(100.0, number)), 2)


class PatternRegimeAnalyzer:
    """Determine which regimes historically produced stronger research outputs."""

    def analyze(
        self,
        regime: MarketRegimeResult,
        compatibility: CompatibilityResult,
    ) -> PatternRegimeAnalysis:
        distribution = {
            regime.regime_state: regime.regime_score,
            "التوافق": compatibility.score,
            "الاستقرار": regime.stability_score,
            "الجودة": regime.quality_score,
        }
        best = max(distribution, key=distribution.get)
        return PatternRegimeAnalysis(
            best_signals=best,
            best_opportunities=best,
            strongest_confluence=compatibility.category,
            highest_stability=regime.regime_state,
            highest_quality_patterns=best,
            distribution=distribution,
        )
