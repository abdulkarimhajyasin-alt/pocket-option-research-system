"""Benchmark scoring engines."""

from __future__ import annotations

from app.strategy_benchmark.models import BenchmarkScore, ComparisonResult


BENCHMARK_STATES = (
    (95, "استثنائية"),
    (85, "قوية جدا"),
    (75, "قوية"),
    (60, "متوسطة"),
    (40, "ضعيفة"),
    (0, "غير مؤهلة"),
)


class BenchmarkScoringEngine:
    """Score quality, consistency, robustness, stability, and repeatability."""

    def score(self, comparison: ComparisonResult) -> BenchmarkScore:
        components = {
            "quality": self._average(
                comparison.signal_quality,
                comparison.opportunity_quality,
                comparison.confluence_quality,
            ),
            "consistency": comparison.consistency_score,
            "robustness": self._average(
                comparison.stability_score,
                comparison.consistency_score,
                comparison.confidence_accuracy,
            ),
            "stability": comparison.stability_score,
            "repeatability": self._repeatability(comparison),
        }
        weights = comparison.profile.weights
        weighted = (
            comparison.readiness_score * weights.get("readiness", 0)
            + comparison.stability_score * weights.get("stability", 0)
            + comparison.consistency_score * weights.get("consistency", 0)
            + comparison.confidence_accuracy * weights.get("confidence", 0)
            + comparison.signal_quality * weights.get("signal", 0)
            + comparison.opportunity_quality * weights.get("opportunity", 0)
            + comparison.confluence_quality * weights.get("confluence", 0)
        )
        score = self._clamp(weighted / max(sum(weights.values()), 0.01))
        state = benchmark_state(score)
        explanation = f"درجة بحثية {state} مبنية على الجودة والاستقرار والتكرارية."
        return BenchmarkScore(
            comparison.profile.profile_id,
            score,
            state,
            explanation,
            components,
        )

    def _repeatability(self, comparison: ComparisonResult) -> float:
        spread = max(comparison.adjusted_metrics.values()) - min(
            comparison.adjusted_metrics.values()
        )
        return self._clamp(100 - spread)

    def _average(self, *values: float) -> float:
        return self._clamp(sum(values) / len(values)) if values else 0.0

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(100.0, float(value))), 2)


def benchmark_state(score: float) -> str:
    """Return Arabic benchmark state for a 0-100 score."""
    for minimum, state in BENCHMARK_STATES:
        if score >= minimum:
            return state
    return "غير مؤهلة"
