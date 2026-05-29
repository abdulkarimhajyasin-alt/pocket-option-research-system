"""Explainable strategy robustness scoring."""

from __future__ import annotations

from app.validation.models import (
    OutOfSampleResult,
    ParameterSweepSummary,
    RobustnessCategory,
    RobustnessScore,
    WalkForwardResult,
)
from app.validation.statistics import clamp


class RobustnessScorer:
    """Scores strategy robustness from explicit validation components."""

    def score(
        self,
        walk_forward: WalkForwardResult | None = None,
        out_of_sample: OutOfSampleResult | None = None,
        sweep: ParameterSweepSummary | None = None,
    ) -> RobustnessScore:
        """Return a 0-100 explainable robustness score."""
        components = {
            "walk_forward_consistency": self._walk_forward_component(walk_forward),
            "out_of_sample_stability": self._out_of_sample_component(out_of_sample),
            "parameter_sensitivity": self._sensitivity_component(sweep),
            "signal_reliability": self._signal_component(walk_forward, out_of_sample),
        }
        score = round(
            components["walk_forward_consistency"] * 0.30
            + components["out_of_sample_stability"] * 0.30
            + components["parameter_sensitivity"] * 0.25
            + components["signal_reliability"] * 0.15,
            2,
        )
        category = self._category(score)
        explanation = [f"{name}: {value:.2f}/100" for name, value in sorted(components.items())]
        explanation.append(f"Category: {category.value}")
        return RobustnessScore(score, category, components, explanation)

    def _walk_forward_component(self, result: WalkForwardResult | None) -> float:
        if result is None or not result.windows:
            return 0.0
        stability = result.stability_metrics
        variation_penalty = (
            float(stability.get("pnl_variation", 0.0)) * 25.0
            + float(stability.get("win_rate_variation", 0.0)) * 40.0
            + float(stability.get("signal_count_variation", 0.0)) * 15.0
        )
        positive_bonus = float(stability.get("positive_window_rate", 0.0)) * 35.0
        return round(clamp(65.0 + positive_bonus - variation_penalty), 2)

    def _out_of_sample_component(self, result: OutOfSampleResult | None) -> float:
        if result is None:
            return 0.0
        return round(clamp(result.stability_score), 2)

    def _sensitivity_component(self, sweep: ParameterSweepSummary | None) -> float:
        if sweep is None or not sweep.results:
            return 0.0
        stable_bonus = 20.0 if sweep.stable_parameter_regions else 0.0
        pnls = [item.result.metrics.net_pnl for item in sweep.results]
        best = max(pnls)
        worst = min(pnls)
        spread = abs(best - worst)
        return round(clamp(85.0 + stable_bonus - spread * 5.0), 2)

    def _signal_component(
        self,
        walk_forward: WalkForwardResult | None,
        out_of_sample: OutOfSampleResult | None,
    ) -> float:
        counts: list[int] = []
        if walk_forward is not None:
            counts.extend(item.test.metrics.signal_count for item in walk_forward.windows)
        if out_of_sample is not None:
            counts.append(out_of_sample.out_of_sample.metrics.signal_count)
        if not counts:
            return 0.0
        average = sum(counts) / len(counts)
        zero_penalty = sum(1 for count in counts if count == 0) * 20.0
        return round(clamp(min(average, 30.0) / 30.0 * 100.0 - zero_penalty), 2)

    def _category(self, score: float) -> RobustnessCategory:
        if score >= 85:
            return RobustnessCategory.RESEARCH_GRADE
        if score >= 70:
            return RobustnessCategory.STRONG
        if score >= 50:
            return RobustnessCategory.MODERATE
        if score >= 30:
            return RobustnessCategory.WEAK
        return RobustnessCategory.VERY_WEAK
