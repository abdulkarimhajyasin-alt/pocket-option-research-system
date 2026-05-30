"""Strategy profile comparator."""

from __future__ import annotations

from typing import Any

from app.strategy_benchmark.models import BenchmarkProfile, ComparisonResult


class StrategyComparator:
    """Compare profiles using upstream research outputs."""

    def compare(
        self,
        profiles: tuple[BenchmarkProfile, ...],
        inputs: dict[str, Any],
    ) -> tuple[ComparisonResult, ...]:
        metrics = self._base_metrics(inputs)
        return tuple(self._compare_profile(profile, metrics) for profile in profiles)

    def _compare_profile(
        self,
        profile: BenchmarkProfile,
        metrics: dict[str, float],
    ) -> ComparisonResult:
        thresholds = profile.thresholds
        adjusted = {
            key: self._clamp(value + self._profile_adjustment(profile, key, thresholds))
            for key, value in metrics.items()
        }
        return ComparisonResult(
            profile=profile,
            readiness_score=adjusted["readiness"],
            stability_score=adjusted["stability"],
            consistency_score=adjusted["consistency"],
            confidence_accuracy=adjusted["confidence"],
            signal_quality=adjusted["signal"],
            opportunity_quality=adjusted["opportunity"],
            confluence_quality=adjusted["confluence"],
            adjusted_metrics=adjusted,
        )

    def _base_metrics(self, inputs: dict[str, Any]) -> dict[str, float]:
        signal = inputs.get("signal_summary", {})
        performance = inputs.get("performance_summary", {})
        opportunity = inputs.get("opportunity_summary", {})
        timeframe = inputs.get("timeframe_summary", {})
        confluence = inputs.get("confluence_summary", {})
        lifecycle = inputs.get("lifecycle_summary", {})
        readiness = inputs.get("readiness_summary", {})
        return {
            "readiness": self._pick(
                readiness,
                "readiness_score",
                "score",
                default=65.0,
            ),
            "stability": self._average(
                self._pick(readiness, "stability_score", default=60.0),
                self._pick(performance, "stability_score", default=58.0),
                self._pick(lifecycle, "average_quality", default=62.0),
            ),
            "consistency": self._average(
                self._pick(timeframe, "average_confirmation", default=60.0),
                self._pick(confluence, "average_confluence", default=60.0),
            ),
            "confidence": self._pick(
                performance,
                "confidence_accuracy",
                "average_confidence",
                default=60.0,
            ),
            "signal": self._pick(signal, "average_quality", "quality_score", default=62.0),
            "opportunity": self._pick(
                opportunity,
                "average_qualification",
                "average_score",
                default=61.0,
            ),
            "confluence": self._pick(
                confluence,
                "average_confluence",
                "average_score",
                default=60.0,
            ),
        }

    def _profile_adjustment(
        self,
        profile: BenchmarkProfile,
        metric: str,
        thresholds: dict[str, float],
    ) -> float:
        minimum = thresholds.get("minimum_score", 60.0)
        stability_minimum = thresholds.get("minimum_stability", 55.0)
        if profile.profile_id == "current":
            return 0.0
        if profile.profile_id == "conservative":
            return 4.0 if metric in {"stability", "consistency"} else -1.0
        if profile.profile_id == "balanced":
            return 2.0 if minimum >= 65 else 0.0
        if profile.profile_id == "aggressive":
            return 4.0 if metric in {"opportunity", "confluence"} else -2.0
        if profile.profile_id == "experimental":
            return 3.0 if metric == "confidence" else -3.0
        return (minimum + stability_minimum) / 100.0

    def _pick(self, payload: Any, *keys: str, default: float) -> float:
        if not isinstance(payload, dict):
            return default
        for key in keys:
            value = payload.get(key)
            if isinstance(value, dict):
                value = value.get("score")
            if value is not None:
                return self._clamp(value)
        return default

    def _average(self, *values: float) -> float:
        return self._clamp(sum(values) / len(values)) if values else 0.0

    def _clamp(self, value: Any) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = 0.0
        return round(max(0.0, min(100.0, number)), 2)
